from random import randint
from datetime import datetime, timedelta

from Groot.Database.models.ClientAdvisorModel import ClientAdvisor
from Groot.Database.models.ClientModel import Client
from Groot.Database.models.Session import Session
from Groot.Logging.config.LoggingFunctions import log_warning, log_info, log_error, print_info
from Groot.Services.ResponseService.RequestResponseService import APIObjectsResponse


class SessionAdministration():

    @staticmethod
    def save_one_time_login(username, data):
        try:
            session_id = data['session_id']
            password_client = data['password_client']
            uuid_client = data['uuid']
            valid_until = data['valid_until']
        except:
            print("Error in SessionAdministration.py line 37")
            log_error("/generate_id got the wrong data fields")
            return APIObjectsResponse.create_generic_response(400, "/generate_id got the wrong data fields")

        # check if the user has the authority to generate a new session_id
        advisor_db = ClientAdvisor.find_by_username(username)

        # if no client_advisor exists or has not been accepted
        if not (advisor_db or advisor_db.accepted):
            log_warning(f"The Advisor {username} made an unauthorized request and was denied")
            return APIObjectsResponse.create_generic_response(406, 'Not Authorized')

        client_db = Client.find_by_uuid(uuid_client)

        # check if the client exists
        if not client_db:
            log_warning(
                f"The Advisor {username} tried to generate a one time password for a non-existing user with uuid {uuid_client}")
            return APIObjectsResponse.create_generic_response(406, 'Not Authorized')

        now = datetime.now()
        valid_timestamp = now + timedelta(hours=valid_until)

        client_db.session_password = password_client
        client_db.session_id = session_id
        client_db.valid_until = valid_timestamp
        client_db.advisor_OTP_username = username
        client_db.save()

        log_info(f"Client with sessionID {session_id} was saved. Valid until: {valid_timestamp}")
        print_info(f"Client with sessionID {session_id} was saved. Valid until: {valid_timestamp}")

        return APIObjectsResponse.create_generic_data_response(202, "Session ID saved", "session",
                                                               {"uuid": uuid_client,
                                                                'session_id': session_id,
                                                                'valid_until': valid_timestamp})

    @staticmethod
    def generate_4digit_session_id(min=1000, max=9999):
        rand = randint(min, max)

        # check if uuid already exists
        while Client.query.filter_by(session_id=rand).first() is not None:
            rand = randint(min, max)

        return APIObjectsResponse.create_generic_data_response(200, "Session ID created", "session_id", rand)

    @staticmethod
    def initialize_session(client, advisor):
        possible_old_session = Session.find_first_active_sessions_by_client_and_advisor(client, advisor)

        if possible_old_session:
            return

        print_info("Creating a new session entry/tuple in the database")

        # get start and stop time
        start_time = datetime.now()

        # create session (and setting stop time to start time)
        current_session = Session(
            transcript="",
            start_time=datetime.now(),
            stop_time=datetime.now(),
            client=client,
            client_advisor=advisor,
            completed=False
        )
        current_session.save()
        # update advisor and client with the new session entity (for bidirectional database)
        advisor_sessions = advisor.get_sessions()
        advisor_sessions.append(current_session)
        advisor.sessions = advisor_sessions
        advisor.update()

        client_sessions = client.get_sessions()
        client_sessions.append(current_session)
        client.sessions = client_sessions
        client.update()
