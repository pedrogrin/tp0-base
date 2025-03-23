from common.utils import store_bets, Bet, load_bets, has_won
import logging

def process_batch_bets(bet_msg):
    """
    Process a batch of bets from a client.
    """
    bets, bets_amount = parse_bets(bet_msg)
    if bets is None:
        logging.info(f"action: apuesta_recibida | result: fail | cantidad: {bets_amount}")
        return
    store_bets(bets)
    logging.info(f"action: apuesta_recibida | result: success | cantidad: {bets_amount}")
    answer_msg = f"recieved: {bets[0].agency}-{bets_amount}\n"
    return answer_msg

def parse_bets(bets_msg):
    """
    Parse the batch of bets message
    Expected format: TICKET,agency,firstname,lastname,document,birthdate_number\n
    """
    bets = []
    parsed_bets = bets_msg.split('\n')
    bets_amount = len(parsed_bets) - 1
    for parsed_bet in parsed_bets:
        if parsed_bet == 'BATCH_DONE':
            break
        bet = parse_bet(parsed_bet)
        if bet is not None:
            bets.append(bet)
        else:
            return None, bets_amount

    return bets, bets_amount

def parse_bet(bet_msg):
    """
    Parse the bet message
    Expected format: TICKET,agency,firstname,lastname,document,birthdate,number
    """
    bet_data = bet_msg.split(',')
    if len(bet_data) != 7 or bet_data[0] != 'TICKET':
        logging.info(f"action: parse_bet | result: fail | msg: {bet_msg}")
        return None
    return Bet(bet_data[1], bet_data[2], bet_data[3], bet_data[4], bet_data[5], bet_data[6])

def check_winners():
    """
    Check if there are winners in the lottery.
    """
    winners = {}
    for bet in load_bets():
        agency = str(bet.agency)
        if agency not in winners:
            winners[agency] = "WINNERS"
        if has_won(bet):
            winners[agency] += f",{bet.document}"
    
    return winners

