from common.utils import store_bets, Bet
import logging

def process_bet(client_socket):
    """
    Process a bet from a client.
    """
    # Receive the bet from the client
    bet_msg = read_all_bet_msg(client_socket)
    addr = client_socket.getpeername()
    logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {bet_msg}')
    bet = parse_bet(bet_msg)
    if bet is None:
        return
    store_bets([bet])
    logging.info(f"action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}")
    answer_msg = f"recieved: {bet.agency}-{bet.document}-{bet.number}\n"
    answer_agency(client_socket, answer_msg)

def process_batch_bets(client_socket):
    """
    Process a batch of bets from a client.
    """
    bet_msg = read_all_bet_msg(client_socket)
    bets, bets_amount = parse_bets(bet_msg)
    if bets is None:
        logging.info(f"action: apuesta_recibida | result: fail | cantidad: {bets_amount}")
        return
    store_bets(bets)
    logging.info(f"action: apuesta_recibida | result: success | cantidad: {bets_amount}")
    answer_msg = f"recieved: {bets[0].agency}-{bets_amount}\n"
    answer_agency(client_socket, answer_msg)


def parse_bets(bets_msg):
    """
    Parse the batch of bets message
    Expected format: TICKET,agency,firstname,lastname,document,birthdate_number;
    """
    bets = []
    parsed_bets = bets_msg.rstrip(';')
    bets_amount = len(parsed_bets)
    for bet_msg in parsed_bets:
        bet = parse_bet(bet_msg)
        if bet is not None:
            bets.append(bet)
        else:
            return None, bets_amount

    return bets, bets_amount

    
def read_all_bet_msg(client_socket, buffer_size=1024):
    """
    Read all the message from the client socket
    """
    data_bytes = b''
    while True:
        chunk = client_socket.recv(buffer_size)
        if not chunk:
            break
        data_bytes += chunk
        if b'\n' in chunk:
            break
    return data_bytes.rstrip().decode('utf-8')

def parse_bet(bet_msg):
    """
    Parse the bet message
    Expected format: TICKET,agency,firstname,lastname,document,birthdate_number
    """
    bet_data = bet_msg.split(',')

    if len(bet_data) != 7 or bet_data[0] != 'TICKET':
        logging.info(f"action: parse_bet | result: fail | msg: {bet_msg}")
        return None
    
    return Bet(bet_data[1], bet_data[2], bet_data[3], bet_data[4], bet_data[5], bet_data[6])

def answer_agency(client_socket, answer_msg):
    """
    Answer the agency with the result of the bet
    """
    data_bytes = answer_msg.encode('utf-8')
    client_socket.sendall(data_bytes)
