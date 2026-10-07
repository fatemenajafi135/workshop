"""One expense, and how to split it fairly."""

from dataclasses import dataclass


@dataclass
class Expense:
    description: str
    payer: str
    amount: int  # in cents
    participants: list[str]


def split_equal(amount: int, n: int) -> list[int]:
    """Split `amount` cents into `n` shares that add up exactly to `amount`.

    Cents that can't be split evenly go to the first shares, one each:
        split_equal(1000, 3) -> [334, 333, 333]
    """
    if n < 1:
        raise ValueError("need at least one person to split between")
    share, leftover = divmod(amount, n)
    return [share + 1 if i < leftover else share for i in range(n)]
