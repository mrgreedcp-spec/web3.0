"""Salary normalisation is pure logic and needs no network."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from remote_jobs_scraper.salary import from_numeric, parse_salary_text


def test_range_in_thousands():
    s = parse_salary_text("$120k - $150k")
    assert s is not None
    assert s.min_annual_usd == 120_000
    assert s.max_annual_usd == 150_000
    assert s.currency == "USD"


def test_plain_range_with_commas():
    s = parse_salary_text("USD 100,000 to 130,000 per year")
    assert s.min_annual_usd == 100_000
    assert s.max_annual_usd == 130_000


def test_hourly_is_annualised():
    s = parse_salary_text("$80 per hour")
    assert s.best == 80 * 2080


def test_monthly_is_annualised():
    s = parse_salary_text("€8000 / month")
    # 8000 * 12 months * EUR->USD rate
    assert round(s.best) == round(8000 * 12 * 1.08)


def test_currency_conversion():
    s = parse_salary_text("£90,000")
    assert round(s.best) == round(90_000 * 1.27)


def test_no_salary_returns_none():
    assert parse_salary_text("Competitive salary, equity") is None
    assert parse_salary_text("") is None
    assert parse_salary_text(None) is None


def test_strict_ignores_noise_without_money_signal():
    # In strict mode "401k" with no currency/keyword is not a salary.
    assert parse_salary_text("Great 401k match and PTO", strict=True) is None
    # A genuine signal still parses in strict mode.
    s = parse_salary_text("Salary: 401k retirement, base $140,000", strict=True)
    assert s is not None and s.best == 401_000


def test_from_numeric_orders_min_max():
    s = from_numeric(150000, 100000, "USD")
    assert s.min_annual_usd == 100_000
    assert s.max_annual_usd == 150_000


def test_from_numeric_hourly():
    s = from_numeric(50, 70, "USD", period="hour")
    assert s.min_annual_usd == 50 * 2080
    assert s.max_annual_usd == 70 * 2080


def test_from_numeric_none():
    assert from_numeric(None, None) is None
