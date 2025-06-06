import logging
import json

from fastapi import Request, APIRouter
from fastapi.responses import PlainTextResponse

import config
import nats_client


logger = logging.getLogger('uvicorn.app')
logger.setLevel(logging.DEBUG)

router = APIRouter()


@router.get(config.MESSENGER_WEBHOOK_ENDPOINT)
async def verify_webhook(request: Request):
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")
    if hub_verify_token == config.MESSENGER_VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge, status_code=200)
    return "Invalid verification token", 403


@router.post(config.MESSENGER_WEBHOOK_ENDPOINT)
async def handle_webhook(request: Request):
    logger.debug("Received a POST request")

    nc = await nats_client.NatsClient.get_instance(logger)
    data = await request.json()
    logger.debug(f"Request body: {data}")

    if "entry" in data:
        for entry in data["entry"]:
            messaging = entry.get("messaging", [])
            for message_event in messaging:
                subject = f"{config.MESSENGER_NATS_SUBJECT_PREFIX}.message"
                await nc.publish(subject, json.dumps(message_event).encode("utf-8"))
                await nc.flush()

    return "ok", 200
