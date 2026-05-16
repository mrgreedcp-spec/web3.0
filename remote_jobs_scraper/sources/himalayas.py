"""Himalayas — https://himalayas.app/jobs/api (public JSON, no key)."""

from __future__ import annotations

from typing import Iterable

from ..models import Job
from ..salary import from_numeric
from .base import Source

API = "https://himalayas.app/jobs/api"


class Himalayas(Source):
    name = "himalayas"

    def __init__(self, *args, limit: int = 200, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit = limit

    def fetch(self) -> Iterable[Job]:
        data = self.get_json(API, params={"limit": self.limit})
        for item in data.get("jobs", []):
            locations = item.get("locationRestrictions") or []
            yield Job(
                title=item.get("title", "").strip(),
                company=item.get("companyName", "").strip(),
                url=item.get("applicationLink") or item.get("guid", ""),
                source=self.name,
                location=", ".join(locations) if locations else "Remote",
                category=", ".join(item.get("categories", []) or []),
                published=item.get("pubDate", ""),
                tags=item.get("seniority", []) or [],
                salary=from_numeric(
                    item.get("minSalary"),
                    item.get("maxSalary"),
                    currency=item.get("salaryCurrency", "USD"),
                ),
            )
