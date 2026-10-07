"""A plain-text summary of a group, ready to paste into a group chat."""

from splitter.balances import balances
from splitter.group import Group
from splitter.money import format_eur
from splitter.settle import settle_up


def summary(group: Group) -> str:
    current = balances(group)
    lines = [group.name, ""]
    for person, balance in current.items():
        if balance > 0:
            lines.append(f"{person} is owed {format_eur(balance)}")
        elif balance < 0:
            lines.append(f"{person} owes {format_eur(-balance)}")
        else:
            lines.append(f"{person} is settled up")

    lines += ["", "To settle up:"]
    transfers = settle_up(current)
    for t in transfers:
        lines.append(f"  {t.sender} pays {t.receiver} {format_eur(t.amount)}")
    if not transfers:
        lines.append("  nothing to do")
    return "\n".join(lines)
