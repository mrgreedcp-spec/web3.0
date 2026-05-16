"""Normalised job record shared across every source."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .salary import Salary


@dataclass
class Job:
    title: str
    company: str
    url: str
    source: str
    location: str = ""
    category: str = ""
    job_type: str = ""
    published: str = ""
    tags: list[str] = field(default_factory=list)
    salary: Salary | None = None

    @property
    def salary_usd(self) -> float | None:
        return self.salary.best if self.salary else None

    def to_dict(self) -> dict:
        data = asdict(self)
        if self.salary is None:
            data["salary"] = None
        else:
            data["salary"] = {
                "min_annual_usd": self.salary.min_annual_usd,
                "max_annual_usd": self.salary.max_annual_usd,
                "currency": self.salary.currency,
                "raw": self.salary.raw,
            }
        data["salary_usd"] = self.salary_usd
        return data
