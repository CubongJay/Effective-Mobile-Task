"""In-memory admin-granted document permissions (not persisted)."""

from typing import Dict

EXTRA_PERMISSIONS: Dict[int, Dict[int, Dict]] = {}
