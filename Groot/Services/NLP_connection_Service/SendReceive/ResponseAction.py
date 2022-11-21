from datetime import datetime

from Groot.Database.models.ClientAdvisorModel import ClientAdvisor
from Groot.Database.models.ClientModel import Client
from Groot.Database.models.CurrentQueue import Queue
from Groot.Database.models.Session import Session
from Groot.Extensions.DatabaseExtension import app, socket_io
from Groot.Logging.config.LoggingFunctions import log_info, log_error
from Groot.Services.Consultation.VisualizationService import VisualizationService


class Strategy_Message:
    def __init__(self, data, current_ack, ack, username, uuid, client_id, strategy=None):

        """take price and discount strategy"""
        self.strategy = strategy
        self.client_id = client_id
        self.__data = data
        self.current_ack = current_ack
        self.target_ack = ack
        self.username = username
        self.uuid = uuid
        self.default_data = {
            "transcription_end": self.transcription_end,
            "text": self.text,
            "active": self.active,
            "passive": self.passive,
            "transcription_start": self.transcription_start,
        }

    def transcription_end(self):
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    def transcription_start(self):
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    def text(self):
        return ""

    def active(self):
        return []

    def passive(self):
        return []

    def data(self, *args):
        current_data_level = self.__data
        nr_args = len(args)

        for i, arg in enumerate(args):
            if arg in current_data_level:
                current_data_level = current_data_level[arg]
            else:
                return self.default_data[args[-1]]()

            if nr_args == i + 1:
                return current_data_level

    def react_to_message(self):
        self.strategy(self)


# ==============================
# functions that decide the action to take by the backend in response to a message from the NLP
def empty_byte(strategy):
    log_info(f"Empty byte was received: socket connection broken")


def check_ack(strategy):
    log_info(f"Message was send properly") if str(strategy.current_ack) == str(strategy.target_ack) \
        else log_error("An error in NLP occurred, no ACK was received or ACK is not correct (check_ack function")


def check_ack_and_add_session_to_db(strategy):
    """receives acknowledgement from NLP and adds the session to the database if the ack is correct."""

    if str(strategy.current_ack) == str(strategy.target_ack):
        log_info(f"Message was send properly")

        # add new session to database
        with app.app_context():
            # get client and advisor
            client = Client.find_by_uuid(strategy.client_id)
            advisor = ClientAdvisor.find_by_uuid(strategy.uuid)

            current_session = Session.find_first_active_sessions_by_client_and_advisor(client, advisor)


def store_data(strategy):
    """function executed when patterns/terms are received from NLP.
    Sends the terms to the frontend and appends the partial transcript to the current transcript."""

    log_info(f"The Mic heard/recognized this: {strategy.data}")
    print("active: " + str(strategy.data('active')) + " passive: " + str(strategy.data('passive')))

    active_patterns = strategy.data('active')
    passive_patterns = strategy.data('passive')
    recognized_patterns = active_patterns + passive_patterns

    pattern = Queue(client_advisor=strategy.username, terms=recognized_patterns)
    print(f"\nnew terms/patterns:")
    print(pattern.terms)

    with app.app_context():
        # store the things into the database
        pattern, changed_flag = pattern.save()

        if changed_flag:
            # emit an event for the frontend to listen to if a new event appeared
            __send_passive_financial_terms_to_frontend(pattern, strategy.uuid, strategy.client_id)

        if len(active_patterns) > 0:
            __send_active_financial_terms_to_frontend(active_patterns, strategy.uuid, strategy.client_id)

    __update_session_transcript(strategy)


def stop_mic_handle_transcript(strategy):
    if str(strategy.current_ack) == str(strategy.target_ack):
        log_info(f"Message was send properly to NLP")

        __update_session_transcript(strategy)

    else:
        log_error(
            "An error in NLP occurred, no ACK was received or ACK is not correct (check_ack_and_add_session_to_db function")


# ========================
# helper functions

def __send_passive_financial_terms_to_frontend(patterns, uuid, client_id):
    log_info(f"The backend sends the following financial terms to the frontend {patterns.terms}")
    socket_io.emit('keywordsServerSent', {"pattern": patterns.terms}, room=str(client_id))


def __send_active_financial_terms_to_frontend(patterns, uuid, client_id):
    log_info(f"The backend sends the following financial terms to the frontend {patterns}")

    for pattern in patterns:
        result = VisualizationService.get_mock_vizualization(client_id, uuid, pattern)
        print("Result emmiting in active mode")
        # result = {'message': 'Successfully requested for Stock', 'TermVisualization': {'term': {'subject': 'Stock', 'description': "A stock is a general term used to describe the ownership certificates of any company. A share, on the other hand, refers to the stock certificate of a particular company. Holding a particular company's share makes you a shareholder.", 'long_description': "Stocks are of two types—common and preferred. The difference is while the holder of the former has voting rights that can be exercised in corporate decisions, the later doesn't. However, preferred shareholders are legally entitled to receive a certain level of dividend payments before any dividends can be issued to other shareholders.", 'synonyms': ['']}, '': -0.5041446570787063, 'plot_data': {'max': 96816.47602313313, 'min': 10400.0, 'plot_values': [{'Date': '1990-12-01', 'Value': 10400.0}, {'Date': '1991-01-01', 'Value': 10784.990794909825}, {'Date': '1991-02-01', 'Value': 11870.782861180529}]
        #     ,'x_axis_label': 'Date', 'y_axis_label': 'Value', 'description': {
        #         'share_class_name': 'self.description.share_class_name', 'ISIN': 'self.description.ISIN',
        #         'risk_profile': 'self.description.risk_profile'}, 'plot_type': 'SCATTERPLOT'}}}
        # print("______________________________________________________________")

        socket_io.emit('getVisualization_response', result, room=str(client_id))


def __update_session_transcript(strategy):
    """Update the session with the new partial transcript."""

    with app.app_context():
        # get client and advisor
        client = Client.find_by_uuid(strategy.client_id)
        advisor = ClientAdvisor.find_by_uuid(strategy.uuid)

        current_session = Session.find_first_active_sessions_by_client_and_advisor(client, advisor)

        if current_session is None:
            raise Exception("No active (i.e. completed=False) session found, but expected to find an active session")

        # update the session with new transcript and stop time
        current_session.transcript = f'{current_session.transcript} {strategy.data("text")}'
        current_session.stop_time = datetime.strptime(strategy.data("metadata", 'transcription_end'),
                                                      '%d/%m/%Y %H:%M:%S')

        # make changes of the session persistent in the database
        current_session.update()
        # print_info(f"\nUpdated session with new transcript:")
        # print(current_session.transcript)


# mapping of 'type' of the response message to the function that handles it
Response2Action = {
    'start_mic': check_ack_and_add_session_to_db,  # used for starting the mic
    'stop_mic': stop_mic_handle_transcript,
    'pattern': store_data,
    'empty_byte': empty_byte,
}
