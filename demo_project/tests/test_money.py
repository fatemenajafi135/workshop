import pytest

from splitter.money import format_eur, to_cents


@pytest.mark.parametrize(
    "text, cents",
    [("12.50", 1250), ("12.5", 1250), ("12", 1200), ("0.05", 5), (" 7.05 ", 705), ("12,50", 1250)],
)
def test_to_cents(text, cents):
    assert to_cents(text) == cents


def test_to_cents_rejects_negative_amounts():
    with pytest.raises(ValueError):
        to_cents("-3.00")


def test_to_cents_rejects_fractions_of_a_cent():
    with pytest.raises(ValueError):
        to_cents("1.005")


@pytest.mark.parametrize(
    "cents, text",
    [(1250, "€12.50"), (1205, "€12.05"), (5, "€0.05"), (0, "€0.00"), (-340, "-€3.40")],
)
def test_format_eur(cents, text):
    assert format_eur(cents) == text
