import socket
import logging
import signal
from common.loteria import process_batch_bets

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

        for client in self.active_sockets_clients:
            client.close()
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
            process_batch_bets(client_sock)
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
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
