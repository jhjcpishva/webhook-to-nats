package main

import (
	"fmt"
	"log"
	"sync"

	"github.com/nats-io/nats.go"
)

var (
	nc   *nats.Conn
	once sync.Once
)

func getNats(logger *log.Logger) (*nats.Conn, error) {
	var err error
	once.Do(func() {
		url := fmt.Sprintf("nats://%s:%s", NatsHost, NatsPort)
		nc, err = nats.Connect(url, nats.Name("go-webhook-nats-client"))
		if err == nil {
			logger.Println("Connected to NATS server")
		}
	})
	return nc, err
}
