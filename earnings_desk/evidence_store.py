"""Shared, citation-addressable report memory."""
import re

from .models import Evidence


class EvidenceStore:
    def __init__(self, text: str):
        self.items: dict[str, Evidence] = {}
        for index, raw in enumerate(re.split(r"(?<=[.!?])\s+|\n+", text.strip()), start=1):
            line = " ".join(raw.split())
            if line:
                source_id = f"S{index:02d}"
                self.items[source_id] = Evidence(source_id, line)

    def search(self, *terms: str) -> list[Evidence]:
        terms = tuple(term.lower() for term in terms)
        return [item for item in self.items.values() if any(t in item.text.lower() for t in terms)]

    def get(self, source_id: str) -> Evidence | None:
        return self.items.get(source_id)
