import os

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
KOKORO_FAST_API_HOST = os.getenv("KOKORO_FAST_API_HOST")
KOKORO_FAST_API_IGNORE_SSL = os.getenv("KOKORO_FAST_API_IGNORE_SSL", "false").lower() == "true"

PORT = int(os.getenv("PORT", "8000"))
