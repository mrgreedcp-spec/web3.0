"""Shared HTTP plumbing for source adapters."""

from __future__ import annotations

import logging
from typing import Iterable

import requests

from ..models import Job

logger = logging.getLogger("remote_jobs_scraper")

USER_AGENT = (
    "remote-jobs-scraper/1.0 (+https://github.com/mrgreedcp-spec/web3.0)"
)
DEFAULT_TIMEOUT = 25


class Source:
    """Base class for a single job board adapter.

    Subclasses implement ``fetch`` and yield :class:`Job` records.
    Network and parsing failures are isolated per source by
    :meth:`safe_fetch` so one dead board never aborts the run.
    """

    name: str = "base"

    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()
        self.session.headers.setdefault("User-Agent", USER_AGENT)

    def get_json(self, url: str, **kwargs) -> dict | list:
        resp = self.session.get(url, timeout=DEFAULT_TIMEOUT, **kwargs)
        resp.raise_for_status()
        return resp.json()

    def get_text(self, url: str, **kwargs) -> str:
        resp = self.session.get(url, timeout=DEFAULT_TIMEOUT, **kwargs)
        resp.raise_for_status()
        return resp.text

    def fetch(self) -> Iterable[Job]:  # pragma: no cover - abstract
        raise NotImplementedError

    def safe_fetch(self) -> list[Job]:
        try:
            jobs = list(self.fetch())
            logger.info("%s: fetched %d jobs", self.name, len(jobs))
            return jobs
        except Exception as exc:  # noqa: BLE001 - isolate per source
            logger.warning("%s: failed (%s)", self.name, exc)
            return []
