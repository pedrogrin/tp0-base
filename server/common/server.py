import socket
import logging
import signal
from common.loteria import process_batch_bets, check_winners

class Server:
    def __init__(self, port, listen_backlog, clients_size):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.active_sockets_clients = []
        self.clients_size = clients_size
        self.clients_done = {}

        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, _frame):
        """
        Signal handler for graceful shutdown
        """
        logging.info(f"action: signal_handler | result: success | signal: {signum}")
        self._server_socket.close()
        logging.info("action: close server socket | result: success | server: closed")

        for client_socket in self.active_sockets_clients:
            self.__delete_socket_from_active(client_socket)
            logging.info("action: close client socket | result: success | client: closed")

        exit(0)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # TODO: Modify this program to handle signal to graceful shutdown
        # the server
        while True:
            client_sock = self.__accept_new_connection()
            self.active_sockets_clients.append(client_sock)
            self.__handle_client_connection(client_sock)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg = self.__read_all_bet_msg(client_sock)
            if 'ALL_BETS_DONE' in msg:
                self.__add_agency_done(msg, client_sock)
                self.__check_all_agencies_done()
            else:
                answer_msg = process_batch_bets(msg)
                self.__answer_socket(client_sock, answer_msg)
                self.__delete_socket_from_active(client_sock)
        except Exception as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
    
    @staticmethod
    def __read_all_bet_msg(client_socket, buffer_size=1024):
        """
        Read all the message from the client socket
        """
        data_bytes = b''
        while True:
            chunk = client_socket.recv(buffer_size)
            if not chunk:
                break
            data_bytes += chunk
            if b'BATCH_DONE' in chunk or b'ALL_BETS_DONE' in chunk:
                break
        return data_bytes.rstrip().decode('utf-8')
    
    @staticmethod
    def __answer_socket(client_socket, answer_msg):
        """
        Answer the socket with the result of the bet
        """
        answer_msg += "\n"
        data_bytes = answer_msg.encode('utf-8')
        client_socket.sendall(data_bytes)

    def __add_agency_done(self, msg, client_socket):
        """Parse msg of type AGENCY_DONE,agency"""
        agency = msg.split(',')[1]
        self.clients_done[agency] = client_socket
    
    def __check_all_agencies_done(self):
        if len(self.clients_done) == self.clients_size:
            winners = check_winners()
            for agency, winners in winners.items():
                if agency in self.clients_done:
                    self.__answer_socket(self.clients_done[agency], winners)
                    self.__delete_socket_from_active(self.clients_done[agency])
            self.clients_done = {}
            logging.info("action: sorteo | result: success")

    def __delete_socket_from_active(self, client_socket):
        """Delete client socket from active_sockets_clients"""
        client_socket.close()
        if client_socket in self.active_sockets_clients:
            self.active_sockets_clients.remove(client_socket)
