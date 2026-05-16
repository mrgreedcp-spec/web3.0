"""RemoteOK — https://remoteok.com/api (public JSON, no key).

The first array element is a legal/usage notice rather than a job and
is skipped. Jobs are remote by definition on this board.
"""

from __future__ import annotations

from typing import Iterable

from ..models import Job
from ..salary import from_numeric, parse_salary_text
from .base import Source

API = "https://remoteok.com/api"


class RemoteOK(Source):
    name = "remoteok"

    def fetch(self) -> Iterable[Job]:
        data = self.get_json(API)
        for item in data:
            if not isinstance(item, dict) or "position" not in item:
                continue
            salary = from_numeric(
                item.get("salary_min"),
                item.get("salary_max"),
                currency="USD",
            ) or parse_salary_text(item.get("description"), strict=True)
            yield Job(
                title=item.get("position", "").strip(),
                company=item.get("company", "").strip(),
                url=item.get("url", ""),
                source=self.name,
                location=item.get("location") or "Remote",
                tags=item.get("tags", []) or [],
                published=item.get("date", ""),
                salary=salary,
            )
