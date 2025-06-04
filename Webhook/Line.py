import logging

from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import PlainTextResponse

import config
from fastapi import Header, HTTPException
from linebot.v3 import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import (
    MessagingApi,
    Configuration,
    ApiClient,
    ReplyMessageRequest,
    TextMessage
)


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
line_bot_api = MessagingApi(ApiClient(configuration))


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    """Echo the text message back to the user."""
    try:
        logger.debug(f"Received message: {event.message.text}")
        result = line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)],
            )
        )
        logger.debug(f"Reply result: {result}")
    except Exception:
        logger.exception("Failed to reply message")
