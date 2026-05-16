"""Arbeitnow — https://www.arbeitnow.com/api/job-board-api (public JSON).

No structured salary field; salary, when present, is parsed from the
job description text.
"""

from __future__ import annotations

import re
from typing import Iterable

from ..models import Job
from ..salary import parse_salary_text
from .base import Source

API = "https://www.arbeitnow.com/api/job-board-api"
_TAG_RE = re.compile(r"<[^>]+>")


class Arbeitnow(Source):
    name = "arbeitnow"

    def fetch(self) -> Iterable[Job]:
        data = self.get_json(API)
        for item in data.get("data", []):
            if not item.get("remote"):
                continue
            description = _TAG_RE.sub(" ", item.get("description", ""))
            yield Job(
                title=item.get("title", "").strip(),
                company=item.get("company_name", "").strip(),
                url=item.get("url", ""),
                source=self.name,
                location=item.get("location", "") or "Remote",
                job_type=", ".join(item.get("job_types", []) or []),
                tags=item.get("tags", []) or [],
                published=str(item.get("created_at", "")),
                salary=parse_salary_text(description, strict=True),
            )
