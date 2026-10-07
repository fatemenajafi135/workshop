"""Converting between text like "12.50" and integer cents."""


def to_cents(text: str) -> int:
    """Parse a euro amount like "12.50", "12.5", "12" or "12,50" into cents."""
    text = text.strip().replace(",", ".")
    if text.startswith("-"):
        raise ValueError(f"amount cannot be negative: {text!r}")
    euros, _, decimals = text.partition(".")
    if len(decimals) > 2:
        raise ValueError(f"amount has more than 2 decimals: {text!r}")
    return int(euros or "0") * 100 + int(decimals.ljust(2, "0"))


def format_eur(cents: int) -> str:
    """Format cents for people: 1205 -> "€12.05", -340 -> "-€3.40"."""
    sign = "-" if cents < 0 else ""
    euros, rest = divmod(abs(cents), 100)
    return f"{sign}€{euros}.{rest:02d}"
