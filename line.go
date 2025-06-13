package main

import (
	"encoding/json"
	"log"

	"github.com/gin-gonic/gin"
	line "github.com/line/line-bot-sdk-go/v7/linebot"
)

func registerLineRoutes(r *gin.Engine, logger *log.Logger) {
	group := r.Group(LineWebhookPrefix)
	group.POST(LineWebhookEndpoint, lineWebhook)
}

func lineWebhook(c *gin.Context) {
	logger := c.MustGet("logger").(*log.Logger)
	nc, err := getNats(logger)
	if err != nil {
		logger.Println(err)
		c.String(500, "NATS error")
		return
	}

	bot, err := line.New(LineChannelSecret, LineChannelAccessToken)
	if err != nil {
		logger.Println(err)
		c.String(500, "LINE error")
		return
	}

	events, err := bot.ParseRequest(c.Request)
	if err != nil {
		if err == line.ErrInvalidSignature {
			c.String(400, "Bad signature")
		} else {
			c.String(500, "Parse error")
		}
		return
	}

	for _, event := range events {
		switch event.Type {
		case line.EventTypeMessage:
			subject := LineNatsSubjectPrefix + ".message"
			body, _ := json.Marshal(event)
			nc.Publish(subject, body)
		case line.EventTypeFollow:
			subject := LineNatsSubjectPrefix + ".follow"
			body, _ := json.Marshal(event)
			nc.Publish(subject, body)
		case line.EventTypeUnfollow:
			subject := LineNatsSubjectPrefix + ".unfollow"
			body, _ := json.Marshal(event)
			nc.Publish(subject, body)
		}
		nc.Flush()
	}

	c.String(200, "OK")
}
