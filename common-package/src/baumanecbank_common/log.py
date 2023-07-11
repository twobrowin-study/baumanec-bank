import asyncio
import logging
from logging.handlers import QueueHandler
from queue import SimpleQueue as Queue

Log = logging.getLogger("asyncio")
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s; %(levelname)s; %(message)s",
                              "%Y-%m-%d %H:%M:%S")
ch.setFormatter(formatter)
Log.addHandler(ch)

class LocalQueueHandler(QueueHandler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.enqueue(record)
        except asyncio.CancelledError:
            raise
        except Exception:
            self.handleError(record)

queue = Queue()
root = logging.getLogger()

handlers: list[logging.Handler] = []

handler = LocalQueueHandler(queue)
root.addHandler(handler)
for h in root.handlers[:]:
    if h is not handler:
        root.removeHandler(h)
        handlers.append(h)

listener = logging.handlers.QueueListener(
    queue, *handlers, respect_handler_level=True
)
listener.start()
