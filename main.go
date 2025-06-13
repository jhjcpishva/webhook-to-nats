package main

import (
	"log"

	"github.com/gin-gonic/gin"
)

func main() {
	logger := log.New(gin.DefaultWriter, "", log.LstdFlags)

	if !WebhookUseMessenger && !WebhookUseLine {
		logger.Fatal("No webhook service to host")
	}

	r := gin.Default()
	r.Use(func(c *gin.Context) {
		c.Set("logger", logger)
	})

	if WebhookUseMessenger {
		registerMessengerRoutes(r, logger)
	}
	if WebhookUseLine {
		registerLineRoutes(r, logger)
	}

	err := r.Run(":" + Port)
	if err != nil {
		logger.Fatal(err)
	}
}
