# web3.0 — Remote Jobs Scraper

Aggregates **high-paying remote jobs** from multiple public job boards,
normalises salaries to an annual USD figure, filters by a minimum
threshold, and exports the results as a table, JSON, or CSV.

## Sources

All sources use public, key-free endpoints:

| Source           | Endpoint                                  | Salary data        |
| ---------------- | ----------------------------------------- | ------------------ |
| Remotive         | `remotive.com/api/remote-jobs`            | free-text salary   |
| RemoteOK         | `remoteok.com/api`                        | numeric min/max    |
| Himalayas        | `himalayas.app/jobs/api`                  | numeric min/max    |
| We Work Remotely | `weworkremotely.com/remote-jobs.rss`      | parsed from text   |
| Arbeitnow        | `arbeitnow.com/api/job-board-api`         | parsed from text   |

A failure in one source (network error, layout change, rate limit)
never aborts the run — that source is skipped and the rest continue.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
# High-paying jobs (>= $120k/yr), top 20 as a table
python -m remote_jobs_scraper --min-salary 120000 --limit 20

# Only engineering roles, JSON to a file
python -m remote_jobs_scraper --keywords engineer python rust \
    --format json --output jobs.json

# Restrict to specific sources, CSV output
python -m remote_jobs_scraper --sources remoteok himalayas --format csv

# Include roles whose salary could not be parsed
python -m remote_jobs_scraper --include-unknown-salary
```

### As a library

```python
from remote_jobs_scraper import scrape

jobs = scrape(min_salary_usd=150_000, keywords=["staff", "principal"])
for j in jobs:
    print(j.title, j.company, j.salary_usd)
```

## Salary normalisation

Salaries arrive in many shapes (`$120k–$150k`, hourly rates, EUR/GBP,
explicit min/max fields). They are all converted to an estimated
**annual USD** value so a single `--min-salary` threshold works across
boards. Hourly rates are annualised at 2080 h/yr, monthly at 12×, and
non-USD currencies use static approximate FX rates (order-of-magnitude
filtering only — not live rates). Free-text parsing in description
fields runs in strict mode so noise like `401k` is not mistaken for a
salary.

## Tests

```bash
python -m pytest tests/        # or: pip install pytest
```

The salary-normalisation logic is covered by `tests/test_salary.py`
(pure logic, no network required).

## Note on network access

When run inside a restricted environment (e.g. Claude Code on the web
with an allowlist network policy), the job-board domains may be blocked
and every source will report a `403`. The scraper degrades gracefully
and exits cleanly. Run it locally, or configure a network policy that
permits the source domains, to fetch live data. See
<https://code.claude.com/docs/en/claude-code-on-the-web> for how
environment network policies are configured.
