# Build stage
FROM golang:1.24 AS builder
WORKDIR /src
COPY go.mod .
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /bin/webhook-to-nats

# Final stage
FROM scratch
COPY --from=builder /bin/webhook-to-nats /webhook-to-nats
ENTRYPOINT ["/webhook-to-nats"]
