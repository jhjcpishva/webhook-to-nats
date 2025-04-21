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
            self.logger.debug(f"📤 Sent Response: {res.status_code!r}, {res.text!r}", )
        return res


    async def send_text_message(self, recipient_id, text):
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text},
            "messaging_type": "RESPONSE"
        }
        return await self.send_payload(payload)
