package main

import (
	"os"
)

func getEnv(key, defaultVal string) string {
	if v, ok := os.LookupEnv(key); ok {
		return v
	}
	return defaultVal
}

var (
	WebhookUseMessenger = getEnv("WEBHOOK_USE_MESSENGER", "false") == "true"
	WebhookUseLine      = getEnv("WEBHOOK_USE_LINE", "false") == "true"

	MessengerVerifyToken       = os.Getenv("MESSENGER_VERIFY_TOKEN")
	MessengerWebhookPrefix     = getEnv("MESSENGER_WEBHOOK_PREFIX", "/messenger")
	MessengerWebhookEndpoint   = getEnv("MESSENGER_WEBHOOK_ENDPOINT", "/webhook")
	MessengerNatsSubjectPrefix = getEnv("MESSENGER_NATS_SUBJECT_PREFIX", "webhook.messenger")

	LineChannelAccessToken = os.Getenv("LINE_CHANNEL_ACCESS_TOKEN")
	LineChannelSecret      = os.Getenv("LINE_CHANNEL_SECRET")
	LineWebhookPrefix      = getEnv("LINE_WEBHOOK_PREFIX", "/line")
	LineWebhookEndpoint    = getEnv("LINE_WEBHOOK_ENDPOINT", "/webhook")
	LineNatsSubjectPrefix  = getEnv("LINE_NATS_SUBJECT_PREFIX", "webhook.line")

	NatsHost = getEnv("NATS_HOST", "localhost")
	NatsPort = getEnv("NATS_PORT", "4222")

	Port = getEnv("PORT", "8000")
)
