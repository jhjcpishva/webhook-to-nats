import logging
import asyncio

from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import PlainTextResponse
from fastapi import Header, HTTPException
from linebot.v3 import WebhookHandler
from linebot.v3.webhooks import MessageEvent, FollowEvent, UnfollowEvent, TextMessageContent
from linebot.v3.messaging import (
    AsyncMessagingApi,
    Configuration,
    ApiClient,
)

import config
import nats_client


logger = logging.getLogger('uvicorn.app')
logger.setLevel(logging.DEBUG)

# FastAPI router for LINE webhook

router = APIRouter()


@router.post(config.LINE_WEBHOOK_ENDPOINT)
async def line_webhook(
    request: Request,
    x_line_signature: str = Header(None),
):
    """Webhook endpoint that echoes received LINE messages."""
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail="Bad Request")
    return PlainTextResponse("OK", status_code=200)


# LINE Messaging API setup
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)
configuration = Configuration(access_token=config.LINE_CHANNEL_ACCESS_TOKEN)
line_bot_api = AsyncMessagingApi(ApiClient(configuration))


@handler.add(MessageEvent)
def handle_message(__event: MessageEvent):
    async def __handle(event: MessageEvent):
        nc = await nats_client.NatsClient.get_instance(logger)
        subject = f"{config.LINE_NATS_SUBJECT_PREFIX}.message"
        await nc.publish(subject, event.to_json().encode("utf-8"))
        await nc.flush()

    asyncio.get_event_loop().create_task(__handle(__event))

@handler.add(FollowEvent)
def handle_follow(__event: FollowEvent):
    async def __handle(event: FollowEvent):
        nc = await nats_client.NatsClient.get_instance(logger)
        subject = f"{config.LINE_NATS_SUBJECT_PREFIX}.follow"
        await nc.publish(subject, event.to_json().encode("utf-8"))
        await nc.flush()

    asyncio.get_event_loop().create_task(__handle(__event))

@handler.add(UnfollowEvent)
def handle_unfollow(__event: UnfollowEvent):
    async def __handle(event: UnfollowEvent):
        nc = await nats_client.NatsClient.get_instance(logger)
        subject = f"{config.LINE_NATS_SUBJECT_PREFIX}.unfollow"
        await nc.publish(subject, event.to_json().encode("utf-8"))
        await nc.flush()

    asyncio.get_event_loop().create_task(__handle(__event))
