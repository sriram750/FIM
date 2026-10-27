import asyncio
import signal
import sys
from app.core.config import settings
from app.core.logging import setup_logging, logger


class EventWorker:
    def __init__(self):
        self.is_running = True

    async def start(self):
        setup_logging()
        logger.info(f"FIM Event & Alert Worker starting on group '{settings.REDIS_GROUP_NAME}'...")
        
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, self.stop)
            except NotImplementedError:
                # Signal handlers not implemented on Windows event loop
                pass

        while self.is_running:
            try:
                # Worker event loop: will process incoming Redis Streams batches
                # Graceful sleep during idle cycles
                await asyncio.sleep(2)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker iteration error: {str(e)}")
                await asyncio.sleep(5)

        logger.info("FIM Event & Alert Worker shutdown completed.")

    def stop(self):
        logger.info("Received stop signal. Shutting down worker gracefully...")
        self.is_running = False


def main():
    worker = EventWorker()
    try:
        asyncio.run(worker.start())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
