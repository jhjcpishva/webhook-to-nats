package main

import (
	"encoding/json"
	"log"

	"github.com/gin-gonic/gin"
)

func registerMessengerRoutes(r *gin.Engine, logger *log.Logger) {
	group := r.Group(MessengerWebhookPrefix)
	group.GET(MessengerWebhookEndpoint, verifyMessenger)
	group.POST(MessengerWebhookEndpoint, handleMessenger)
}

func verifyMessenger(c *gin.Context) {
	token := c.Query("hub.verify_token")
	challenge := c.Query("hub.challenge")
	if token == MessengerVerifyToken {
		c.String(200, challenge)
		return
	}
	c.String(403, "Invalid verification token")
}

func handleMessenger(c *gin.Context) {
	logger := c.MustGet("logger").(*log.Logger)
	nc, err := getNats(logger)
	if err != nil {
		logger.Println(err)
		c.String(500, "NATS error")
		return
	}

	var body map[string]any
	if err := c.BindJSON(&body); err != nil {
		c.String(400, "Bad Request")
		return
	}

	if entries, ok := body["entry"].([]any); ok {
		for _, e := range entries {
			entry, ok := e.(map[string]any)
			if !ok {
				continue
			}
			if msgs, ok := entry["messaging"].([]any); ok {
				for _, m := range msgs {
					msgJSON, _ := json.Marshal(m)
					subject := MessengerNatsSubjectPrefix + ".message"
					nc.Publish(subject, msgJSON)
					nc.Flush()
				}
			}
		}
	}

	c.String(200, "ok")
}
