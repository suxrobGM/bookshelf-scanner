import logging
import sys

COLORS = {
    "DEBUG": "\033[36m",  # cyan
    "INFO": "\033[32m",  # green
    "WARNING": "\033[33m",  # yellow
    "ERROR": "\033[31m",  # red
    "CRITICAL": "\033[1;31m",  # bold red
}
RESET = "\033[0m"
GRAY = "\033[90m"


class ColoredFormatter(logging.Formatter):
    """Log formatter that adds ANSI colors per log level."""

    def format(self, record: logging.LogRecord) -> str:
        color = COLORS.get(record.levelname, "")
        level = f"{color}{record.levelname:<8}{RESET}"
        name = f"{GRAY}{record.name}{RESET}"
        return f"{level} {name} - {record.getMessage()}"


def setup_logging(level: int = logging.INFO) -> None:
    """Configure colored logging for the entire application."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter())

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("ultralytics").setLevel(logging.WARNING)
