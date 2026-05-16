"""Parse heterogeneous salary strings into a comparable annual USD figure.

Job boards expose salary in wildly different shapes: free text
("$120k-$150k"), explicit min/max numbers, hourly rates, non-USD
currencies. We normalise everything to an estimated annual amount in
USD so a single threshold can be applied across all sources.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Rough, intentionally static FX rates. Salary filtering only needs
# order-of-magnitude accuracy, not live rates.
_USD_PER_UNIT = {
    "USD": 1.0,
    "EUR": 1.08,
    "GBP": 1.27,
    "CAD": 0.73,
    "AUD": 0.66,
    "CHF": 1.12,
    "INR": 0.012,
    "SGD": 0.74,
    "BRL": 0.18,
}

_CURRENCY_SYMBOLS = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "₹": "INR",
}

_HOURS_PER_YEAR = 2080  # 40h/week * 52 weeks
_MONTHS_PER_YEAR = 12

_NUMBER_RE = re.compile(
    r"(\d{1,3}(?:[,.\s]\d{3})+|\d+(?:\.\d+)?)\s*([kK])?"
)


@dataclass(frozen=True)
class Salary:
    min_annual_usd: float | None
    max_annual_usd: float | None
    currency: str
    raw: str

    @property
    def best(self) -> float | None:
        """Single value used for threshold comparison and sorting."""
        if self.max_annual_usd is not None:
            return self.max_annual_usd
        return self.min_annual_usd


def _detect_currency(text: str) -> str:
    upper = text.upper()
    for code in _USD_PER_UNIT:
        if code in upper:
            return code
    for symbol, code in _CURRENCY_SYMBOLS.items():
        if symbol in text:
            return code
    return "USD"


_HOURLY_RE = re.compile(r"(per\s*hour|/\s*hr|/\s*hour|hourly|an hour)")
_MONTHLY_RE = re.compile(r"(per\s*month|/\s*mo(?:nth)?\b|monthly|a month)")
_MONEY_KEYWORD_RE = re.compile(
    r"salary|compensation|\bpay\b|\bcomp\b|wage|/\s*yr|per\s*year"
    r"|per\s*annum|annually|annual\b"
)


def _detect_period_multiplier(text: str) -> float:
    lowered = text.lower()
    if _HOURLY_RE.search(lowered):
        return _HOURS_PER_YEAR
    if _MONTHLY_RE.search(lowered):
        return _MONTHS_PER_YEAR
    return 1.0


def _has_money_signal(text: str) -> bool:
    upper = text.upper()
    if any(code in upper for code in _USD_PER_UNIT):
        return True
    if any(sym in text for sym in _CURRENCY_SYMBOLS):
        return True
    lowered = text.lower()
    if _HOURLY_RE.search(lowered) or _MONTHLY_RE.search(lowered):
        return True
    return bool(_MONEY_KEYWORD_RE.search(lowered))


def _to_number(raw: str, k_suffix: str | None) -> float | None:
    cleaned = raw.replace(",", "").replace(" ", "")
    # A trailing ".000" style group is a thousands separator, not decimals.
    if cleaned.count(".") == 1:
        whole, frac = cleaned.split(".")
        if len(frac) == 3 and not k_suffix:
            cleaned = whole + frac
    try:
        value = float(cleaned)
    except ValueError:
        return None
    if k_suffix:
        value *= 1000
    return value


def parse_salary_text(text: str | None, strict: bool = False) -> Salary | None:
    """Extract an annualised USD salary range from free-form text.

    With ``strict=True`` the text must carry an explicit money signal
    (currency, pay period, or a salary keyword) before any number is
    treated as compensation. Use it for description text where bare
    numbers like "401k" or "10x growth" would otherwise be misread.
    """
    if not text:
        return None
    text = text.strip()
    if not text:
        return None
    if strict and not _has_money_signal(text):
        return None

    currency = _detect_currency(text)
    period_mult = _detect_period_multiplier(text)

    numbers: list[float] = []
    for match in _NUMBER_RE.finditer(text):
        value = _to_number(match.group(1), match.group(2))
        if value is None:
            continue
        # Discard noise like a lone "401" from "401k benefits" by
        # ignoring implausibly small annual-equivalent figures.
        annual = value * period_mult
        if annual < 1000:
            continue
        numbers.append(value)

    if not numbers:
        return None

    rate = _USD_PER_UNIT.get(currency, 1.0)
    lo = min(numbers) * period_mult * rate
    hi = max(numbers) * period_mult * rate
    return Salary(
        min_annual_usd=round(lo, 2),
        max_annual_usd=round(hi, 2),
        currency=currency,
        raw=text,
    )


def from_numeric(
    minimum: float | int | None,
    maximum: float | int | None,
    currency: str | None = "USD",
    period: str = "year",
) -> Salary | None:
    """Build a Salary from explicit numeric min/max fields."""
    if minimum is None and maximum is None:
        return None

    currency = (currency or "USD").upper()
    rate = _USD_PER_UNIT.get(currency, 1.0)

    period = (period or "year").lower()
    if period.startswith("hour"):
        mult = _HOURS_PER_YEAR
    elif period.startswith("month"):
        mult = _MONTHS_PER_YEAR
    else:
        mult = 1.0

    def conv(v: float | int | None) -> float | None:
        if v is None:
            return None
        return round(float(v) * mult * rate, 2)

    lo = conv(minimum)
    hi = conv(maximum)
    if lo is not None and hi is not None and lo > hi:
        lo, hi = hi, lo
    return Salary(
        min_annual_usd=lo,
        max_annual_usd=hi,
        currency=currency,
        raw=f"{minimum}-{maximum} {currency}/{period}",
    )
