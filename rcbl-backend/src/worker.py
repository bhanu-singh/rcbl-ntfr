"""arq worker settings.

Run with: uv run arq src.worker.WorkerSettings

Only the process_ocr job is registered for the MVP invoice upload module.
Add future jobs by importing and appending to the `functions` list.
"""

from arq.connections import RedisSettings

from src.config import settings
from src.modules.invoices.jobs import process_ocr


class WorkerSettings:
    """arq WorkerSettings — read by the arq CLI."""

    functions = [process_ocr]

    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)

    # Retry settings
    max_tries = 3
    job_timeout = 120  # seconds — OCR calls can be slow

    # Worker health
    health_check_interval = 30
    health_check_key = "rcbl:worker:health"

    on_startup = None
    on_shutdown = None
