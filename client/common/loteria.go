package common

import (
	"fmt"
	"net"
	"github.com/op/go-logging"
	"bufio"
)


// Ticket de apuesta
type Ticket struct {
	Agency   string
	Name     string
	Lastname string
	Document string
	Birthday string
	Number 	 string
}

func SendTicket(conn net.Conn, ticket Ticket, maxLen int, log *logging.Logger, clientID string) {
	// Send ticket to the server
	bet_msg := fmt.Sprintf("TICKET,%s,%s,%s,%s,%s,%s\n", ticket.Agency, ticket.Name, ticket.Lastname, ticket.Document, ticket.Birthday, ticket.Number)
	if len(bet_msg) > maxLen {
		log.Errorf("action: send_ticket | result: failed | client_id: %v | msg: Ticket too long", clientID)
		return
	}

	data := []byte(bet_msg)
	totalSent := 0
	for totalSent < len(data) {
		n, err := conn.Write(data[totalSent:])
		if err != nil {
			log.Errorf("action: send_ticket | result: failed | error: %v", err)
			return
		}
		totalSent += n
	}
	log.Infof("action: send_ticket | result: success | client_id: %v | msg: Ticket sent", clientID)
	msg, err := bufio.NewReader(conn).ReadString('\n')
	if msg == "" || err != nil {
		log.Errorf("action: apuesta_enviada | result: ERROR | msg: %v | error: %v", msg, err)
		return
	}
	validateAnswer(msg, ticket, log)
}

func validateAnswer(msg string, ticket Ticket, log *logging.Logger) {
	// Validate the server response
	if msg == fmt.Sprintf("recieved: %s-%s-%s\n", ticket.Agency, ticket.Document, ticket.Number) {
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v", ticket.Document, ticket.Number)
	} else {
		log.Errorf("action: apuesta_enviada | result: fail | dni: %v | numero: %v", ticket.Document, ticket.Number)
	}
}

func SendBatchTickets(conn net.Conn, tickets []Ticket, maxLen int, log *logging.Logger, clientID string) {
	// Send all tickets in the batch
	batch_msg := ""
	len_tickets := len(tickets)
	for _, ticket := range tickets {
		batch_msg += fmt.Sprintf("TICKET,%s,%s,%s,%s,%s,%s\n", ticket.Agency, ticket.Name, ticket.Lastname, ticket.Document, ticket.Birthday, ticket.Number)
	}
	batch_msg += "BATCH_DONE"

	if len(batch_msg) > maxLen {
		log.Errorf("action: send_batch | result: failed | client_id: %v | msg: Ticket too long", clientID)
		return
	}
	
	data := []byte(batch_msg)
	totalSent := 0
	for totalSent < len(data) {
		n, err := conn.Write(data[totalSent:])
		if err != nil {
			log.Errorf("action: send_batch | result: failed | error: %v", err)
			return
		}
		totalSent += n
	}
	log.Infof("action: send_batch | result: success | client_id: %v | msg: Ticket sent", clientID)
	msg, err := bufio.NewReader(conn).ReadString('\n')
	if msg == "" || err != nil {
		log.Errorf("action: send_batch | result: ERROR | msg: %v | error: %v", msg, err)
		return
	}
	if msg == fmt.Sprintf("recieved: %s-%d\n", tickets[0].Agency, len_tickets) {
		log.Infof("action: batch_enviado | result: success")
	} else {
		log.Errorf("action: batch_enviado | result: fail")
	}
}
