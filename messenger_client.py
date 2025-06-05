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


async def messenger_llm_responder():
    import asyncio
    import logging
    import json
    from nats.aio.msg import Msg

    import config
    from messenger_client import MessengerClient
    from kokoro_fastapi_client import KokoroFastAPIClient
    from nats_client import NatsClient

    logger = logging.getLogger("nats-subscriber")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(handler)

    messenger_client = MessengerClient(
        access_token=config.MESSENGER_PAGE_ACCESS_TOKEN,
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

    # NatsClient 経由で接続
    nc = await NatsClient.get_instance(logger)

    async def message_handler(msg: Msg):
        subject = msg.subject
        message_event = json.loads(msg.data)
        print(f"[Received on '{subject}']: {message_event}")

        # ここにメッセージ着信時の処理を追加
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

    # サブジェクト "updates" を購読し、メッセージを受信したら message_handler を呼ぶ
    subject = f"{config.MESSENGER_NATS_SUBJECT_PREFIX}.message"
    await nc.subscribe(subject, cb=message_handler)
    logger.debug(f"Subscribed to '{subject}'")

    # 永久待機してメッセージを受け取り続ける
    await asyncio.Event().wait()


if __name__ == "__main__":
    import asyncio
    asyncio.run(messenger_llm_responder())
