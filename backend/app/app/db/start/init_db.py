import logging

from app.db.start.init_langs import init_languages
from app.db.start.mg.init_mg1886 import ImportMgBible
from app.db.start.mg.init_diem import ImportDiemBible

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Creating initial data")
    init_languages()
    ImportMgBible(lang='mg', version="MG1886", )
    ImportDiemBible(lang="mg", version="DIEM", file_encoding="utf-8-sig")
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
