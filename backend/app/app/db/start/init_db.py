import logging

from app.db.start import init_languages
from app.db.start import InitMgBible

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Creating initial data")
    init_languages()
    InitMgBible()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
