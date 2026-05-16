"""Orchestrate sources, deduplicate, and filter by salary/keyword."""

from __future__ import annotations

import concurrent.futures
import logging
from typing import Iterable, Sequence

import requests

from .models import Job
from .sources import ALL_SOURCES

logger = logging.getLogger("remote_jobs_scraper")


def _dedupe(jobs: Iterable[Job]) -> list[Job]:
    seen: set[tuple[str, str]] = set()
    unique: list[Job] = []
    for job in jobs:
        key = (job.title.lower().strip(), job.company.lower().strip())
        if key in seen:
            continue
        seen.add(key)
        unique.append(job)
    return unique


def _matches_keywords(job: Job, keywords: Sequence[str]) -> bool:
    if not keywords:
        return True
    haystack = " ".join(
        [job.title, job.company, job.category, " ".join(job.tags)]
    ).lower()
    return any(kw.lower() in haystack for kw in keywords)


def scrape(
    min_salary_usd: float = 100_000,
    sources: Sequence[str] | None = None,
    keywords: Sequence[str] | None = None,
    require_salary: bool = True,
) -> list[Job]:
    """Collect remote jobs across boards, keeping only high-paying ones.

    ``min_salary_usd`` is compared against the annualised USD estimate.
    Jobs without a parseable salary are dropped when ``require_salary``
    is set (the default, since the goal is *high-paying* roles).
    """
    selected = sources or list(ALL_SOURCES)
    unknown = [s for s in selected if s not in ALL_SOURCES]
    if unknown:
        raise ValueError(f"Unknown source(s): {', '.join(unknown)}")

    session = requests.Session()
    adapters = [ALL_SOURCES[name](session=session) for name in selected]

    collected: list[Job] = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(adapters) or 1
    ) as pool:
        for jobs in pool.map(lambda a: a.safe_fetch(), adapters):
            collected.extend(jobs)

    keywords = keywords or []
    result: list[Job] = []
    for job in _dedupe(collected):
        if not _matches_keywords(job, keywords):
            continue
        salary = job.salary_usd
        if salary is None:
            if require_salary:
                continue
        elif salary < min_salary_usd:
            continue
        result.append(job)

    result.sort(key=lambda j: j.salary_usd or 0, reverse=True)
    logger.info(
        "Collected %d jobs, %d match filters",
        len(collected),
        len(result),
    )
    return result
