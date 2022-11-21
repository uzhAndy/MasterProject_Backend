import pickle

from Groot.Logging.config.LoggingFunctions import log_warning
from Groot.Services.NLP_connection_Service.SendReceive.ResponseAction import Response2Action, Strategy_Message
from Groot.Services.NLP_connection_Service.SocketTCP.ClientSocket import socket, clientSock


class ReceiveFromNLP:

    @staticmethod
    def __decode(obj):
        return pickle.loads(obj)

    @staticmethod
    def receive(ack, username=None, uuid=None, client_id=None):
        """receives data from the NLP and executes the corresponding action (Response2Action)."""

        try:
            # print("Waiting to receive message")
            data = clientSock.get_socket().recv(4096)

            data_decoded = {'type': 'empty_byte', 'ack': 'ACK', 'data': ""}
            if data != b'':
                data_decoded = ReceiveFromNLP.__decode(data)
            # print(f"acknowledgement received: {data_decoded}")

            action = Response2Action[data_decoded['type']]
            strategy = Strategy_Message(
                data_decoded['data'],
                data_decoded['ack'],
                ack, username, uuid, client_id, action
            )

            return strategy.react_to_message()

        # if the message cannot be received the connection failed
        except socket.error as e:
            print("Error in ReceiveFromNLPController.py line 37")
            print(e)
            log_warning("NLP did not respond or backend closed connection (user just left consultation page)")
            raise ConnectionRefusedError('Custom error NLP; could not acknowledge')
