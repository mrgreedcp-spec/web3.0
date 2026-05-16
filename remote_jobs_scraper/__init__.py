"""Aggregate high-paying remote jobs from multiple public job boards."""

from .models import Job
from .scraper import scrape

__all__ = ["Job", "scrape"]
