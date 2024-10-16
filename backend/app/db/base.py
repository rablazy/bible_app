# Import all the models, so that Base has them before being
# imported by Alembic
from app.models.bible import Bible, Book, Chapter, Language, Verse  # noqa

from .base_class import Base  # noqa
