import json
import time

from Groot.Database.models.ClientAdvisorModel import ClientAdvisor
from Groot.Database.models.ClientModel import Client
from Groot.Database.models.FinancialJargon import FinancialJargon
from Groot.Database.models.MicrophoneModel import Microphone
from Groot.Database.models.Session import Session
from Groot.Database.models.Speech2TextModuleModel import Speech2TextModuleModel
from Groot.Logging.config.LoggingFunctions import log_info, log_warning, print_info
from Groot.Services.NLP_connection_Service.SendReceive.ReceiveFromNLPController import ReceiveFromNLP
from Groot.Services.NLP_connection_Service.SendReceive.SendToNLPController import SendToNLP
from Groot.Services.NLP_connection_Service.SocketTCP.ClientSocket import clientSock
from Groot.Services.NLP_connection_Service.Thread.ListenThread import ListenThread


class NLP_connection:
    ListenThreadSingleton = ListenThread()

    @staticmethod
    def get_all_microphones():
        """returns all microphones from the Microphone table in the database"""
        list_microphones = Microphone.query.all()

        return json.dumps([mic.serialize() for mic in list_microphones])

    @staticmethod
    def start(username, uuid, client_id):
        """starts socket connection to the NLP controller in a new thread (ListenThread) if not already running. Also, sends the financial keywords (incl. synonyms) from the database to the NLP controller and waits for the acknowledgment."""
        print_info("Mic start command received")
        try:
            # check if MIC is running (if it is we cannot start it again)
            # check needs to be done with the alive variable and not with request_status
            if NLP_connection.ListenThreadSingleton.is_alive():
                return {'message': 'NLP connection is already running'}, 200

            # Connect the socket to the port where the server is listening
            ca = ClientAdvisor.find_by_uuid(uuid=uuid)
            mic = ca.microphone
            print_info("Using this mic: " + str(mic.name))

            server_address = (mic.ip, mic.port)

            print_info(f'connecting to {server_address[0]} port {server_address[1]}')

            clientSock.get_socket().connect(server_address)

            # get all key_words (cluster risk and synonyms) from database
            all_terms = NLP_connection.get_key_words()
            # create message to send to NLP, incl. the module name
            start_message = {
                'module': Speech2TextModuleModel.get_selected(),
                'all_terms': all_terms,
            }
            # send them to nlp server, this starts the session
            SendToNLP.start_mic(start_message)
            ReceiveFromNLP.receive('ACK', username, uuid, client_id)

            # start thread
            NLP_connection.ListenThreadSingleton.initialize_listen_thread(username, uuid, client_id)

            print_info("Started Successfully")

        except Exception as e:
            print("Error in NLP_connection.py line 65")
            print(e)
            # try to enable reconnection -> if you press the start button again it
            # tries to reestablish the connection
            clientSock.close_connection(NLP_connection.ListenThreadSingleton)
            log_warning('NLP could not be reached')
            raise ConnectionRefusedError('NLP could not be reached')

    @staticmethod
    def stop():
        print_info("Mic stop command received")
        try:
            # check if MIC is running (if it is we cannot stop it again)
            if not NLP_connection.ListenThreadSingleton.is_alive():
                print("a")
                print_info('Mic is NOT running')
                return {'message': 'NLP_connection is NOT running'}, 200

            print("b")
            # sends order to stop to mic -> the ACK is received by the thread
            # do not wait for ACK here otherwise the thread will throw an error
            SendToNLP.stop_mic()
            print("c")
            # delay closing the thread and socket, to allow last part of the transcript to arrive at the backend
            time.sleep(.5)

            log_info('Closing Listen-thread on Backend-side in NLP_connection.stop() function')
            print("d")
            NLP_connection.ListenThreadSingleton.stop_thread()

            print("e")
            log_info('Closing Socket on Backend-side in NLP_connection.stop() function')
            clientSock.close_connection()
            print("f")

            print_info("Stopped Successfully")

        except Exception as e:
            print("Error in NLP_connection.py line 97")
            print(e)
            log_warning('Closing Socket on Backend-side in NLP_connection.stop() function -> error occurred')
            clientSock.close_connection(NLP_connection.ListenThreadSingleton)
            return {'message': 'Socket could not cut connection to NLP'}, 406

    @staticmethod
    def end_session(client_uuid, advisor_uuid):
        print_info("Mic end_session command received")

        # if the mic was not stopped yet, stop it
        # if NLP_connection.ListenThreadSingleton.is_alive():
        #     print("waiting for the mic to be stopped")
        NLP_connection.stop()

        # retrieve the client and advisor from the database
        client = Client.find_by_uuid(client_uuid)
        advisor = ClientAdvisor.find_by_uuid(advisor_uuid)

        # retrieve the active session of the client and advisor
        session = Session.find_first_active_sessions_by_client_and_advisor(client, advisor)

        # when the session was not started/no session was found
        if not session:
            return

        # set the session to inactive, i.e. completed
        session.completed = True
        session.update()

        print_info("Session ended and completed successfully")

    @staticmethod
    def get_key_words():
        """
        Return a dictionary with the terms as keys and the synonyms as values
        """
        terms = FinancialJargon.get_all_terms()

        term2syn = {}

        for term in terms:
            if not term.subject in term2syn:
                term2syn[term.subject] = term.synonyms

        return term2syn
