import asyncio
import logging
from collections import deque
from datetime import datetime, timezone


class MongoLogHandler(logging.Handler):
    """
    Async-safe logging handler that buffers records and flushes them
    to the MongoDB `system_logs` collection every 5 seconds.

    Usage:
        # After MongoDB connects (in lifespan startup):
        await mongo_log_handler.start(db)

        # On shutdown:
        await mongo_log_handler.stop()
    """

    def __init__(self, max_buffer: int = 2000):
        super().__init__()
        self._buffer: deque = deque(maxlen=max_buffer)
        self._db = None
        self._running = False
        self._task = None

    def emit(self, record: logging.LogRecord):
        """Called synchronously by Python's logging machinery."""
        try:
            doc = {
                "timestamp": datetime.now(timezone.utc),
                "level": record.levelname,
                "message": self.format(record),
                "logger": record.name,
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "exc_info": self.formatException(record.exc_info) if record.exc_info else None,
            }
            self._buffer.append(doc)
        except Exception:
            self.handleError(record)

    async def start(self, db):
        """Start the background flush loop. Call after MongoDB is connected."""
        self._db = db
        self._running = True
        self._task = asyncio.create_task(self._flush_loop())

    async def stop(self):
        """Flush remaining records and stop the background task."""
        self._running = False
        if self._task:
            self._task.cancel()
        await self._flush()

    async def _flush_loop(self):
        while self._running:
            await asyncio.sleep(5)
            await self._flush()

    async def _flush(self):
        if not self._db or not self._buffer:
            return
        docs = []
        while self._buffer:
            docs.append(self._buffer.popleft())
        if docs:
            try:
                await self._db.system_logs.insert_many(docs, ordered=False)
            except Exception:
                pass  # Never let the log handler crash the app


mongo_log_handler = MongoLogHandler()
