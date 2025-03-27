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
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
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
		// Intentar crear la conexión al servidor
		if err := c.createClientSocket(); err != nil {
			log.Errorf("action: start_loop | result: fail | client_id: %v | msg: Could not connect to server, shutting down", c.config.ID)
			c.cleanup()
			return // Salir del bucle si no se puede conectar
		}

		// Enviar mensaje al servidor
		_, err := fmt.Fprintf(
			c.conn,
			"[CLIENT %v] Message N°%v\n",
			c.config.ID,
			msgID,
		)
		if err != nil {
			log.Errorf("action: send_message | result: fail | client_id: %v | error: %v", c.config.ID, err)
			c.cleanup()
			continue // Saltar a la siguiente iteración si falla el envío
		}

		// Leer respuesta del servidor
		msg, err := bufio.NewReader(c.conn).ReadString('\n')

		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v", c.config.ID, err)
			continue // Continuar si falla la recepción
		}

		log.Infof("action: receive_message | result: success | client_id: %v | msg: %v", c.config.ID, msg)

		// Esperar antes del próximo mensaje
		time.Sleep(c.config.LoopPeriod)
	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
