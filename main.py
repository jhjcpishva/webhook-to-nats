import logging

from fastapi import FastAPI

import config

logger = logging.getLogger('uvicorn.app')
logger.setLevel(logging.DEBUG)


app = FastAPI(debug=True)

if config.WEBHOOK_USE_LINE:
    from Webhook.Line import router as line_router
    app.include_router(
        line_router, prefix=config.MESSENGER_WEBHOOK_PREFIX, tags=["messenger"])

if config.WEBHOOK_USE_MESSENGER:
    from Webhook.FacebookMessenger import router as fb_router
    app.include_router(
        fb_router, prefix=config.LINE_WEBHOOK_PREFIX, tags=["line"])


if __name__ == "__main__":
    import uvicorn

    if not config.WEBHOOK_USE_LINE and not config.WEBHOOK_USE_MESSENGER:
        raise Exception("No webhook service to host.")

    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
