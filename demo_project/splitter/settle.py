"""Turning balances into a list of payments that settles everyone."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Transfer:
    sender: str
    receiver: str
    amount: int  # in cents


def settle_up(balances: dict[str, int]) -> list[Transfer]:
    """Who pays whom, so that everyone ends at zero.

    Greedy: the person who owes the most pays the person who is owed the most,
    until nobody owes anything. Usually few transfers, not always the fewest.
    """
    if sum(balances.values()) != 0:
        raise ValueError("balances must add up to zero")
    open_balances = {person: b for person, b in balances.items() if b != 0}
    transfers = []
    while open_balances:
        debtor = min(open_balances, key=lambda person: open_balances[person])
        creditor = max(open_balances, key=lambda person: open_balances[person])
        amount = min(-open_balances[debtor], open_balances[creditor])
        transfers.append(Transfer(debtor, creditor, amount))
        open_balances[debtor] += amount
        open_balances[creditor] -= amount
        open_balances = {person: b for person, b in open_balances.items() if b != 0}
    return transfers
