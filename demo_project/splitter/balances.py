"""Who is up and who is down in a group."""

from splitter.expenses import split_equal
from splitter.group import Group


def balances(group: Group) -> dict[str, int]:
    """Net balance per member, in cents.

    Positive: the group owes this person money.
    Negative: this person owes the group money.
    All balances add up to zero.
    """
    result = {person: 0 for person in group.members}
    for expense in group.expenses:
        result[expense.payer] += expense.amount
        shares = split_equal(expense.amount, len(expense.participants))
        for person, share in zip(expense.participants, shares):
            result[person] -= share
    return result
