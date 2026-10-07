"""The fewest transfers that settle a group: exact, but slow.

settle_up() in settle.py is greedy and fast, but sometimes uses more transfers
than needed. This one tries every way to settle and keeps the shortest.
The lab's job: make it faster without changing what it returns.
"""

from splitter.settle import Transfer


def fewest_transfers(balances: dict[str, int]) -> list[Transfer]:
    """A shortest list of transfers after which everyone's balance is zero."""
    if sum(balances.values()) != 0:
        raise ValueError("balances must add up to zero")
    people = [person for person, balance in balances.items() if balance != 0]
    amounts = [balances[person] for person in people]
    best: list[Transfer] | None = None

    def search(transfers: list[Transfer]) -> None:
        nonlocal best
        first = next((i for i, amount in enumerate(amounts) if amount != 0), None)
        if first is None:
            if best is None or len(transfers) < len(best):
                best = list(transfers)
            return
        # Settle `first` completely with someone on the other side, then go on.
        for other in range(first + 1, len(amounts)):
            if amounts[first] * amounts[other] < 0:
                amount = amounts[first]
                if amount < 0:
                    transfers.append(Transfer(people[first], people[other], -amount))
                else:
                    transfers.append(Transfer(people[other], people[first], amount))
                amounts[other] += amount
                amounts[first] = 0
                search(transfers)
                amounts[first] = amount
                amounts[other] -= amount
                transfers.pop()

    search([])
    return best or []
