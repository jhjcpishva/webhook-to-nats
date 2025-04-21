import logging

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

import config
from messenger_client import MessengerClient

logger = logging.getLogger('uvicorn.app')
logger.setLevel(logging.DEBUG)


app = FastAPI(debug=True)

messenger_client = MessengerClient(
    access_token=config.PAGE_ACCESS_TOKEN,
    logger=logger
)


@app.get("/webhook")
async def verify_webhook(request: Request):
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")
    if hub_verify_token == config.VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge, status_code=200)
    return "Invalid verification token", 403


@app.post("/webhook")
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
                        res = await messenger_client.send_attachment(
                            recipient_id=sender_id,
                            filename="meow_praise.png",
                            file=open("path/to/image.png", "rb"),
                            attachment_type="image",
                            mime_type="image/png",
                        )
                    except Exception as e:
                        logger.exception(e)
    return "ok", 200


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
