import threading

from Groot.Services.NLP_connection_Service.SendReceive.ReceiveFromNLPController import ReceiveFromNLP


class ListenThread():
    __instance = None
    __lock = threading.Lock()

    # implemented single pattern thread safe according to with help of the __new__ dunder method: https://medium.com/analytics-vidhya/how-to-create-a-thread-safe-singleton-class-in-python-822e1170a7f6
    def __new__(cls):
        # if the instance is not created yet, create it
        if not cls.__instance:
            with cls.__lock:
                # additional check because another thread might have created the instance before the lock was acquired
                if not cls.__instance:
                    print("------------ Creating new instance of ListenThread ------------")
                    cls.__instance = super(ListenThread, cls).__new__(cls)

        # else, or after creating it, return the instance
        return cls.__instance

    def __init__(self, *args, **kwargs):
        super(ListenThread, self).__init__(*args, **kwargs)
        self.stop_event = threading.Event()
        self.thread = None

    # function using _stop function
    def stop_thread(self):
        # sets the stop event flag -> but might not stop immediately
        self.stop_event.set()

        # cleaner but solution: https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread
        # waits here until thread was terminated
        self.thread.join()
        # clean up
        print(f"-------------- Thread stopped {self.thread.name} ----------------")
        self.thread = None
        self.stop_event.clear()

    def reset_thread(self):
        self.thread = None

    def is_alive(self):
        # print(f"\n-------------- Thread alive {False if self.thread == None else self.thread.is_alive()} ----------------")
        # print(f"thread: {self.thread}")
        # if not self.thread == None:
        #     print(f"thread.is_alive(): {self.thread.is_alive()}")
        return False if self.thread == None else self.thread.is_alive()

    def initialize_listen_thread(self, username, uuid, client_id):
        if not self.thread:
            self.thread = threading.Thread(target=self.__start_thread,
                                           args=(username, uuid, client_id))
            self.thread.start()
            print(f"-------------- Thread started {self.thread.name} ----------------")

    def __start_thread(self, username, uuid, client_id):

        try:
            # should always listen
            while True:
                # if stop event is set, reactivate it, but exit the function
                if self.stop_event.is_set():
                    self.stop_event.clear()
                    return

                # needs to ACK since it can also receive messages (like stop) from the main thread
                ReceiveFromNLP.receive("ACK", username, uuid, client_id)


        # if the code to cut the connection is faster than
        except ConnectionAbortedError as e:
            print("Error in ListenThread.py line 81")
            print(e)
            print("Receiving patterns failed")
            raise ConnectionRefusedError('Could not receive from NLP')
