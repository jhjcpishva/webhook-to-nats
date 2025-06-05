import logging

from fastapi import FastAPI

import config

logger = logging.getLogger('uvicorn.app')
logger.setLevel(logging.DEBUG)


app = FastAPI(debug=True)

if config.WEBHOOK_USE_LINE:
    from Webhook.Line import router
    app.include_router(
        router, prefix=config.LINE_WEBHOOK_PREFIX, tags=["line"])

if config.WEBHOOK_USE_MESSENGER:
    from Webhook.FacebookMessenger import router
    app.include_router(
        router, prefix=config.MESSENGER_WEBHOOK_PREFIX, tags=["messenger"])


if __name__ == "__main__":
    import uvicorn

    if not config.WEBHOOK_USE_LINE and not config.WEBHOOK_USE_MESSENGER:
        raise Exception("No webhook service to host.")

    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
