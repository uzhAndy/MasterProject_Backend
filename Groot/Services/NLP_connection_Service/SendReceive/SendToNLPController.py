import pickle

from Groot.Logging.config.LoggingFunctions import log_info, print_error
from Groot.Services.NLP_connection_Service.SendReceive.ReceiveFromNLPController import ReceiveFromNLP
from Groot.Services.NLP_connection_Service.SocketTCP.ClientSocket import clientSock, socket


class SendToNLP:

    @staticmethod
    def __encode(obj):
        return pickle.dumps(obj)

    @staticmethod
    def __send_to_NLP(message):
        # try to send data
        try:
            log_info(f"The Backend sends this data to NLP {str(message)}")

            # create bytes object from the message
            bytes_message = SendToNLP.__encode(message)

            # send object over the socket
            clientSock.get_socket().send(bytes_message)

        # if the message cannot be sent the connection was not established
        except socket.error as e:
            print("Error in SendToNLPController.py line 27")
            print_error(f"The Backend failed to send {str(message)}")
            print(e)
            raise ConnectionRefusedError('Lost connection to NLP')

    @staticmethod
    def start_mic(start_message):
        """
        start_message = {
            'module': speech2text_module,
            'all_terms': all_terms,
        }
        """
        SendToNLP.__send_to_NLP({'type': 'start_mic', 'data': start_message})

    @staticmethod
    def stop_mic():
        SendToNLP.__send_to_NLP({'type': 'stop_mic', 'data': True})

    @staticmethod
    # it is true it if is already running
    def request_status():
        SendToNLP.__send_to_NLP({'type': 'status', 'data': True})
        return ReceiveFromNLP.receive("True")
