from logging import Logger
import nats
import config


class NatsClient:
    __instance: nats.NATS | None = None

    @classmethod
    async def get_instance(cls, logger: Logger) -> nats.NATS:
        if cls.__instance is None:
            cls.__instance = await nats.connect(
                servers=[f"nats://{config.NATS_HOST}:{config.NATS_PORT}"],
                name="fastppi-webhook-nats-client",
                max_reconnect_attempts=-1,
                reconnect_time_wait=2,
            )
            logger.debug("Connected to NATS server.")
        return cls.__instance
