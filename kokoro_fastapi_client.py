from logging import Logger
import httpx
import config


class KokoroFastAPIClient:
    def __init__(self, logger: Logger):
        self.base_url = config.KOKORO_FAST_API_HOST
        self.logger = logger
        self.verify_ssl = not config.KOKORO_FAST_API_IGNORE_SSL

    async def collect_tts(self, text: str):
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            url = f"{self.base_url}/v1/audio/speech"
            res = await client.post(url, json={
                "input": text,
                "voice": "af_sky",
                "response_format": "mp3",
                "speed": 1,
            })
            self.logger.debug(
                f"💬 TTS Response: {res.status_code!r}", )
            return res
