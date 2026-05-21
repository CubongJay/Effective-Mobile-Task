"""Mock document records (not persisted)."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass
class Document:
    id: int
    title: str
    content: str
    owner_id: int
    created_at: datetime = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()


MOCK_DOCUMENTS: Dict[int, Document] = {
    1: Document(
        id=1,
        title="Django JWT Setup",
        content="Step by step guide to add JWT authentication...",
        owner_id=2,
    ),
    2: Document(
        id=2,
        title="My Python Notes",
        content="List comprehensions, decorators, generators...",
        owner_id=1,
    ),
    3: Document(
        id=3,
        title="Docker Commands",
        content="docker-compose up --build, docker exec...",
        owner_id=1,
    ),
}
