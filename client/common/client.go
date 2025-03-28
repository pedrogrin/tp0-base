package common

import (
	"bufio"
	"fmt"
	"net"
	"time"
	"os/signal"
	"os"
	"syscall"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
	BatchAmount   int
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
	tickets []Ticket
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, tickets []Ticket) *Client {
	client := &Client{
		config: config,
		tickets: tickets,
	}
	client.handleSignals()
	return client
}

// handleSignals for SIGTERM and SIGINT with a gracefylly shutdown
func (c *Client) handleSignals() {
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGTERM, syscall.SIGINT)

	go func() {
		<-sigChan
		log.Infof("action: shutdown | result: success | client_id: %v | msg: Received termination signal", c.config.ID)
		c.cleanup()
		os.Exit(0)
	}()
}

// gracefully shutdown for client resources
func (c *Client) cleanup() {
	if c.conn != nil {
		c.conn.Close()
		log.Infof("action: shutdown | result: success | client_id: %v | msg: Connection closed", c.config.ID)
		c.conn = nil
	}
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Errorf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return err
	}
	c.conn = conn
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	for msgID := 1; msgID <= c.config.LoopAmount; msgID++ {
		// Create the connection the server in every loop iteration. Send an
		c.createClientSocket()

		// TODO: Modify the send to avoid short-write
		fmt.Fprintf(
			c.conn,
			"[CLIENT %v] Message N°%v\n",
			c.config.ID,
			msgID,
		)
		msg, err := bufio.NewReader(c.conn).ReadString('\n')
		c.conn.Close()

		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}

		log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
			c.config.ID,
			msg,
		)

		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}


func (c *Client) SendAllBetsToServer() {
	if c.config.BatchAmount == 0 {
		log.Criticalf("action: send_tickets | result: fail | error: BatchAmount is 0")
		return
	}
	batches := c.splitTicketsBatches()
	if err := c.createClientSocket(); err != nil {
		c.cleanup()
		return // Salir del bucle si no se puede conectar
	}
	for _, batch := range batches {
		SendBatchTickets(c.conn, batch, 8196, log, c.config.ID)
	}
	CheckWinnersWithServer(c.conn, log, c.config.ID)
	c.conn.Close()
}

func (c *Client) splitTicketsBatches() [][]Ticket {
	var batches [][]Ticket

	for i := 0; i < len(c.tickets); i += c.config.BatchAmount {
		end := i + c.config.BatchAmount
		if end > len(c.tickets) {
			end = len(c.tickets)
		}
		batches = append(batches, c.tickets[i:end])
	}
	return batches
}
