import logging
import httpx

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

import config

logger = logging.getLogger('uvicorn.app')
logger.setLevel(logging.DEBUG)


app = FastAPI(debug=True)


async def send_payload(payload: dict):
    url = "https://graph.facebook.com/v22.0/me/messages"
    params = {"access_token": config.PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        res = await client.post(url, params=params, json=payload, headers=headers)
        logger.debug(f"💧 Sent Response: {res.status_code!r}, {res.text!r}", )
    return res


async def send_text_message(recipient_id, text):
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
        "messaging_type": "RESPONSE"
    }
    return await send_payload(payload)


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
                    await send_text_message(sender_id, f"Echo: {text}")

    return "ok", 200


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
