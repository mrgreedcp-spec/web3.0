"""Command-line entry point.

Usage:
    python -m remote_jobs_scraper --min-salary 120000 --format table
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys

from .scraper import scrape
from .sources import ALL_SOURCES


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="remote_jobs_scraper",
        description="Scrape high-paying remote jobs from public job boards.",
    )
    p.add_argument(
        "--min-salary",
        type=float,
        default=100_000,
        help="Minimum annualised salary in USD (default: 100000).",
    )
    p.add_argument(
        "--sources",
        nargs="+",
        choices=sorted(ALL_SOURCES),
        help="Subset of sources to query (default: all).",
    )
    p.add_argument(
        "--keywords",
        nargs="+",
        help="Only keep jobs matching any of these keywords.",
    )
    p.add_argument(
        "--include-unknown-salary",
        action="store_true",
        help="Keep jobs whose salary could not be parsed.",
    )
    p.add_argument(
        "--format",
        choices=("table", "json", "csv"),
        default="table",
        help="Output format (default: table).",
    )
    p.add_argument(
        "--output",
        help="Write output to this file instead of stdout.",
    )
    p.add_argument(
        "--limit",
        type=int,
        help="Cap the number of jobs in the output.",
    )
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Log progress to stderr.",
    )
    return p


def _render_table(jobs) -> str:
    if not jobs:
        return "No matching jobs found."
    lines = []
    for j in jobs:
        s = j.salary_usd
        salary = f"${s:,.0f}" if s else "n/a"
        lines.append(
            f"[{salary:>12}] {j.title}  @ {j.company} "
            f"({j.source}) — {j.location}\n  {j.url}"
        )
    return "\n".join(lines)


def _render_csv(jobs) -> str:
    import io

    buf = io.StringIO()
    fields = [
        "title",
        "company",
        "salary_usd",
        "location",
        "source",
        "category",
        "url",
        "published",
    ]
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for j in jobs:
        writer.writerow(j.to_dict())
    return buf.getvalue()


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(message)s",
    )

    jobs = scrape(
        min_salary_usd=args.min_salary,
        sources=args.sources,
        keywords=args.keywords,
        require_salary=not args.include_unknown_salary,
    )
    if args.limit:
        jobs = jobs[: args.limit]

    if args.format == "json":
        out = json.dumps(
            [j.to_dict() for j in jobs], indent=2, ensure_ascii=False
        )
    elif args.format == "csv":
        out = _render_csv(jobs)
    else:
        out = _render_table(jobs)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(out + "\n")
        print(f"Wrote {len(jobs)} jobs to {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
