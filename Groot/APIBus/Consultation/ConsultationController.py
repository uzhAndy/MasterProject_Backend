import functools

import jwt
from flask import request, abort, Blueprint
from flask_socketio import join_room, leave_room

from Groot.Database.models.ClientAdvisorModel import ClientAdvisor
from Groot.Database.models.ClientModel import Client
from Groot.Database.models.CurrentQueue import Queue
from Groot.Database.models.FinancialJargon import FinancialJargon
from Groot.Database.models.JWT_tokens import TokenBlocklist
from Groot.Extensions.DatabaseExtension import socket_io, db
from Groot.Logging.config.LoggingFunctions import *
from Groot.Services.Consultation.VisualizationService import VisualizationService
from Groot.Services.NLP_connection_Service.NLP_connection import NLP_connection
from Groot.Services.SessionService.SessionAdministration import SessionAdministration as SA
from Groot.Services.UserManagementService.UserManagementService import UserManagementService as UMS

bp = Blueprint('server_communication', __name__)


def check_login(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        bear_token = request.args.get("token", None)[7:]
        decoded_token = {}
        jti = ""
        username = ""
        sid = 0

        if bear_token is None:
            print("Disconnects in check login")
            disconnect()
        else:
            bear_token = bear_token
            try:
                decoded_token = jwt.decode(bear_token, 'Groot', algorithms=["HS256"])
                jti = decoded_token["jti"]
                username = decoded_token["sub"]
                client_id = args[0]['client_id']
                sid = request.sid

            except:
                # if it cannot be decoded then it is not valid
                print("Disconnects in check login error")
                disconnect()
                abort(409)

            used_logout = db.session.query(db.exists().where(TokenBlocklist.jti == jti)).scalar()
            user_exists = db.session.query(db.exists().where(ClientAdvisor.username == username)).scalar()
            client_otp = Client.query.filter_by(session_id=username).first()
            client = Client.find_by_uuid(client_id)
            temp_login_valid = False

            if username.isnumeric() and client_otp:
                temp_login_valid = client_otp.temp_login_valid()
                username = client_otp.advisor_OTP_username
                client = client_otp

            if used_logout or (not user_exists and not temp_login_valid):
                disconnect()
                abort(409)

        return f(username, client, sid, *args, **kwargs)

    return decorated_function


@socket_io.on('connect')
def connect():
    print_info(f'Socket_io (Frontend-Backend) is connected')
    log_info('Socket_io (Frontend-Backend) is connected')


@socket_io.on('disconnect')
def disconnect():
    # stop listening on disconnect
    data = 3
    # clientSock.get_socket().close()
    print_info('Socket_io (Frontend-Backend) is disconnected')
    log_info('Socket_io (Frontend-Backend) is disconnected')


@socket_io.on('initialize')
@check_login
def initialize(username, client, sid, data):
    # logged_in_user_id = data['user_id']

    # the username comes from the wrapper function
    join_room(str(client.uuid))

    # get all current patterns
    current_queue = Queue.query.filter(Queue.client_advisor == username).all()

    # check if there is only one queue
    if len(current_queue) > 1:
        pass
        # print(f"There are too many Queues for the user with id {data['user_id']}")

    if current_queue:
        current_patterns = Queue(client_advisor=username, terms=[])
        current_patterns.save()

    # if the advisor enters a session, empty the queue (i.e. don't empty the queue for all other guests that join with a session id)
    advisor = ClientAdvisor.query.filter_by(username=username).first()
    # if advisor.uuid == logged_in_user_id:
    #   current_queue[0].clear_all()
    current_patterns = current_queue[0].terms

    # get all keywords
    all_patterns = list(map(lambda term: term.subject, FinancialJargon.get_all_terms()))

    # get all mics
    mics = NLP_connection.get_all_microphones()

    # initialize session
    advisor = ClientAdvisor.find_by_username(username)
    SA.initialize_session(client, advisor)

    socket_io.emit("initialize_response",
                   {'message': 'initialize complete',
                    'current_patterns': current_patterns,
                    'all_patterns': all_patterns,
                    'all_mics': mics},
                   room=str(client.uuid))


@socket_io.on("clear_all")
@check_login
def clear_terms(username, client, sid, data):
    pattern = Queue(client_advisor=username, terms=[])
    pattern.clear_all()

    socket_io.emit("request_clear_pattern_response", {'current_patterns': pattern.terms}, room=str(client.uuid))


@socket_io.on("request_pattern")
@check_login
def request_financial_term(username, client, sid, data):
    pattern = Queue(client_advisor=username, terms=data["pattern"])
    user = ClientAdvisor.find_by_username(username)

    pattern, _ = pattern.save()
    socket_io.emit('request_clear_pattern_response', {'current_patterns': pattern.terms}, room=str(client.uuid))

    # get the visualization and send it to room
    # we want to only get the visualization (active view) for the last pattern in the list (i.e. the newest in the queue)
    result = VisualizationService.get_mock_vizualization(client.uuid, user.uuid, pattern.terms[-1])
    socket_io.emit('getVisualization_response', result, room=str(client.uuid))


@socket_io.on("risk_questionnaire_visibility")
@check_login
def risk_questionnaire_visibility(username, client, sid, data):
    client_id = data['client_id']
    visibility = data['visibility']
    socket_io.emit("risk_questionnaire_visibility_response", visibility, room=str(client_id))


@socket_io.on("stop_mic")
@check_login
def stop_mic(username, client, sid, data):
    NLP_connection.stop()
    socket_io.emit("start_stop_mic_response",
                   {"message": "Successful stopped", "running": False}, room=str(client.uuid))


@socket_io.on("start_mic")
@check_login
def start_mic(username, client, sid, data):
    uuid = data['user_id']
    client_id = data['client_id']

    if uuid == client_id:
        uuid, client_id = UMS.get_advisor_client_from_otp(uuid)

    NLP_connection.start(username, uuid, client_id)

    socket_io.emit("start_stop_mic_response", {"message": "Successful started", "running": True}, room=str(client.uuid))


@socket_io.on("set_mics")
@check_login
def update_microphone(username, client, sid, data):
    mic_id = data['mic_id']
    mic_name = data['name']
    """
    expected body:
    {
        "uuid": 9686
        "mic": "Groot 1",
    }

    the response will look like this
    {
    "message": "Successfully updated mic for ClientAdvisor."
    }
    """
    socket_io.emit("set_mics_response", UMS.update_microphone(username, mic_id, mic_name), room=str(client.uuid))


@socket_io.on("leave_consultation")
@check_login
def leave_consultation(username, client, sid, data):
    client_uuid = data['client_id']
    advisor_uuid = data['user_id']

    if advisor_uuid == client_uuid:
        uuid, client_id = UMS.get_advisor_client_from_otp(advisor_uuid)

    NLP_connection.stop()
    NLP_connection.end_session(client_uuid, advisor_uuid)

    leave_room(str(client_uuid))
