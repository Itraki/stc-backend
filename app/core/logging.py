import logging
from app.config import settings

_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

_file_handler = logging.FileHandler(settings.LOG_FILE)
_file_handler.setFormatter(_formatter)

_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(_formatter)

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[_file_handler, _stream_handler]
)

logger = logging.getLogger(__name__)

# MongoDB handler — attached after DB connects (see main.py lifespan).
# Import here so the rest of the app can reference it.
from app.core.mongo_log_handler import mongo_log_handler  # noqa: E402
mongo_log_handler.setFormatter(_formatter)
logging.getLogger().addHandler(mongo_log_handler)
