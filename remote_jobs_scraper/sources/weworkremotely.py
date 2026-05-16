"""We Work Remotely — RSS feed (no public JSON API).

Salary is not a structured field; when present it lives in free text
inside the item description, so it is best-effort parsed.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Iterable

from ..models import Job
from ..salary import parse_salary_text
from .base import Source

FEED = "https://weworkremotely.com/remote-jobs.rss"
_TAG_RE = re.compile(r"<[^>]+>")


class WeWorkRemotely(Source):
    name = "weworkremotely"

    def fetch(self) -> Iterable[Job]:
        root = ET.fromstring(self.get_text(FEED))
        for item in root.iterfind(".//item"):
            title = (item.findtext("title") or "").strip()
            company, _, role = title.partition(":")
            description = item.findtext("description") or ""
            text = _TAG_RE.sub(" ", description)
            yield Job(
                title=(role or title).strip(),
                company=company.strip(),
                url=(item.findtext("link") or "").strip(),
                source=self.name,
                location="Remote",
                category=(item.findtext("category") or "").strip(),
                published=(item.findtext("pubDate") or "").strip(),
                salary=parse_salary_text(text, strict=True),
            )
