# webhook-to-nats

## Overview

- Relays webhook request to NATS server for messaging services such as Messenger and LINE.
- Webhook content will be published to NATS subject such as:
  - `MESSENGER_NATS_SUBJECT_PREFIX` (default: `webhook.messenger`) + `<event>`
    - example: `webhook.messenger.message`
  - `LINE_NATS_SUBJECT_PREFIX` (default: `webhook.line`) + `<event>`
    - example: `webhook.line.message`, `webhook.line.follow`, `webhook.line.unfollow`

## .env

```dotenv
# Enable webhook
WEBHOOK_USE_MESSENGER=true
WEBHOOK_USE_LINE=true

# Messenger webhook url: https://example.com/messenger/webhook
MESSENGER_VERIFY_TOKEN=__set_your_verify_token_here__
MESSENGER_PAGE_ACCESS_TOKEN=...
MESSENGER_WEBHOOK_PREFIX=/messenger
MESSENGER_WEBHOOK_ENDPOINT=/webhook
# webhook will be published to webhook.messenger.message
MESSENGER_NATS_SUBJECT_PREFIX=webhook.messenger

# LINE Messaging webhook url: https://example.com/line/webhook
LINE_CHANNEL_ACCESS_TOKEN=...
LINE_CHANNEL_SECRET=...
LINE_WEBHOOK_PREFIX=/line
LINE_WEBHOOK_ENDPOINT=/webhook
LINE_NATS_SUBJECT_PREFIX=webhook.line

# nats server setting
NATS_HOST=nats-server
NATS_PORT=4222
```

## Run

### Docker

```sh
docker build -t webhook-to-nats -f Dockerfile .
docker run \
  --env-file .env \
  -p 8000:8000 \
  webhook-to-nats
```

### Docker Compose (development)

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    env_file:
      - .env
    ports:
      - "8000:8000"
    develop:
      watch:
        - action: sync
          path: .
          target: /app
        - action: rebuild
          path: go.mod
  nats-server:
    image: nats:latest
    ports:
      - "4222:4222"
```

## Debug – watch the messages

```bash
docker run -it --rm --net=host natsio/nats-box:latest \
  nats -s nats://localhost:4222 sub "webhook.>"
```
