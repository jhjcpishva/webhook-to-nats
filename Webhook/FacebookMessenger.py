import logging
import asyncio
from io import BytesIO

from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import PlainTextResponse

import config
from messenger_client import MessengerClient
from kokoro_fastapi_client import KokoroFastAPIClient


logger = logging.getLogger('uvicorn.app')
logger.setLevel(logging.DEBUG)

router = APIRouter()


messenger_client = MessengerClient(
    access_token=config.PAGE_ACCESS_TOKEN,
    logger=logger
)

tts_client = KokoroFastAPIClient(logger=logger)


async def call_llm(text: str):
    import ollama
    client = ollama.AsyncClient()
    response = await client.chat(
        model="llama3.2:latest",
        messages=[
            {"role": "system", "content": "You are a helpful and friendly assistant. You can only speak in English. Make content for speaking."},
            {"role": "user", "content": text},
        ],
    )
    return response.message.content


@router.get("/webhook")
async def verify_webhook(request: Request):
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")
    if hub_verify_token == config.VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge, status_code=200)
    return "Invalid verification token", 403


@router.post("/webhook")
async def handle_webhook(request: Request):
    logger.debug("Received a POST request")
    logger.debug(f"Request body: {await request.json()}")

    data = await request.json()

    if "entry" in data:
        for entry in data["entry"]:
            messaging = entry.get("messaging", [])
            for message_event in messaging:
                sender_id = message_event["sender"]["id"]
                if "message" in message_event and "text" in message_event["message"]:
                    text = message_event["message"]["text"]
                    # await messenger_client.send_text_message(sender_id, f"Echo: {text}")
                    try:
                        # res = await messenger_client.send_attachment(
                        #     recipient_id=sender_id,
                        #     filename="meow_praise.png",
                        #     file=open("path/to/image.png", "rb"),
                        #     attachment_type="image",
                        #     mime_type="image/png",
                        # )
                        res_llm = await call_llm(text)
                        await messenger_client.send_text_message(sender_id, res_llm)

                        async def _delayed_task():
                            res_tts = await tts_client.collect_tts(res_llm)
                            res = await messenger_client.send_attachment(
                                recipient_id=sender_id,
                                filename="speech.mp3",
                                file=BytesIO(res_tts.content),
                                attachment_type="audio",
                                mime_type="audio/mpeg",
                            )
                        # make response to webhook first, then run LLM and TTS
                        asyncio.create_task(_delayed_task())

                    except Exception as e:
                        logger.exception(e)
    return "ok", 200
