import socket

from Groot.Logging.config.LoggingFunctions import print_info


class ClientSocket:

    def __init__(self):
        self.client_socket = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ClientSocket, cls).__new__(cls)
        return cls.instance

    def __create_socket(self):
        # Create a TCP/IP socket
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def get_socket(self):
        # check if the socket (not connection) is closed
        if not self.client_socket or self.client_socket.fileno() == -1:
            self.client_socket = self.__create_socket()

        return self.client_socket

    def close_connection(self, thread=None):
        if self.client_socket:
            print_info("Close connection")
            # self.client_socket.shutdown(SHUT_RDWR)
            self.client_socket.close()

        # not optimal but safe fix
        # thread keeps running but we reset the pointer.
        if thread:
            thread.reset_thread()

        self.client_socket = None


clientSock = ClientSocket()
