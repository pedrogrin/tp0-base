package common

import (
	"fmt"
	"net"

	"github.com/op/go-logging"
)


// Ticket de apuesta
type Ticket struct {
	Agency   int
	Name     string
	Lastname string
	Document string
	Birthday string
	Number 	 int
}

func sendTicket(conn net.Conn, ticket Ticket maxLen int) {
	// Send ticket to the server
	bet_msg := fmt.Sprintf("%d,%s,%s,%s,%s,%d\n", ticket.Agency, ticket.Name, ticket.Lastname, ticket.Document, ticket.Birthday, ticket.Number)
	if len(bet_msg) > maxLen {
		log.Errorf("action: send_ticket | result: failed | client_id: %v | msg: Ticket too long", c.config.ID)
		return
	}

	data = []byte(bet_msg)
	totalSent := 0
	for totalSent < len(data) {
		n, err := conn.Write(data[totalSent:])
		if err != nil {
			log.Printf("action: send_ticket | result: failed | error: %v", err)
			return fmt.Errorf("failed to send ticket: %w", err)
		}
		totalSent += n
	}
	log.Infof("action: send_ticket | result: success | client_id: %v | msg: Ticket sent", c.config.ID)
	msg, err := bufio.NewReader(conn).ReadString('\n')
	validateAnswer(msg, ticket)
	return msg, err
}

func validateAnswer(msg string, ticket Ticket) {
	// Validate the server response
	if msg == fmt.Sprintf("recieved: %d-%s-%d\n", ticket.Agency, ticket.Document, ticket.Number) {
		log.Infof("action: apuesta_almacenada | result: success | dni: %v} | numero: %v", ticket.Document, ticket.Number)
	} else {
		log.Infof("action: apuesta_almacenada | result: fail | dni: %v} | numero: %v", ticket.Document, ticket.Number)
	}
}
