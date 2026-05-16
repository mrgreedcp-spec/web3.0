"""Remotive — https://remotive.com/api/remote-jobs (public JSON, no key)."""

from __future__ import annotations

from typing import Iterable

from ..models import Job
from ..salary import parse_salary_text
from .base import Source

API = "https://remotive.com/api/remote-jobs"


class Remotive(Source):
    name = "remotive"

    def fetch(self) -> Iterable[Job]:
        data = self.get_json(API)
        for item in data.get("jobs", []):
            yield Job(
                title=item.get("title", "").strip(),
                company=item.get("company_name", "").strip(),
                url=item.get("url", ""),
                source=self.name,
                location=item.get("candidate_required_location", ""),
                category=item.get("category", ""),
                job_type=item.get("job_type", ""),
                published=item.get("publication_date", ""),
                tags=item.get("tags", []) or [],
                salary=parse_salary_text(item.get("salary")),
            )
