import logging

from fastapi import FastAPI

import config
from Webhook.FacebookMessenger import router as fb_router

logger = logging.getLogger('uvicorn.app')
logger.setLevel(logging.DEBUG)


app = FastAPI(debug=True)
app.include_router(fb_router, prefix="/messenger", tags=["messenger"])



if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
