import json
from io import BytesIO
from logging import Logger
import httpx


class MessengerClient:
    def __init__(self, access_token: str, logger: Logger):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/"
        self.logger = logger

    async def send_payload(self, payload: dict):
        url = f"{self.base_url}/v22.0/me/messages"
        params = {"access_token": self.access_token}
        async with httpx.AsyncClient() as client:
            res = await client.post(url, params=params, json=payload)
            self.logger.debug(
                f"📤 Sent Response: {res.status_code!r}, {res.text!r}", )
        return res

    async def send_text_message(self, recipient_id, text):
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text},
            "messaging_type": "RESPONSE"
        }
        return await self.send_payload(payload)

    async def send_attachment(self, recipient_id: str, filename: str, file: BytesIO, attachment_type: str, mime_type: str):
        # url = f"{self.base_url}/v22.0/me/message_attachments"
        url = f"{self.base_url}/v22.0/me/messages"

        if attachment_type not in ["audio", "video", "image", "file"]:
            raise ValueError(f"Invalid attachment type: {attachment_type}")

        data = {
            "recipient": json.dumps({"id": recipient_id}),
            "message": json.dumps({
                "attachment": {
                    "type": attachment_type,
                    "payload": {
                        "is_reusable": False
                    }
                }
            }),
            "messaging_type": "RESPONSE"
        }
        files = {
            "filedata": (filename, file, mime_type),
        }
        params = {"access_token": self.access_token}
        async with httpx.AsyncClient() as client:
            res = await client.post(url, data=data, files=files, params=params)
            self.logger.debug(
                f"📤 Attachment Response: {res.status_code!r}, {res.text!r}", )

        return res
