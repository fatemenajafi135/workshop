"""A group of friends sharing expenses, for example one trip."""

from splitter.expenses import Expense
from splitter.money import to_cents


class Group:
    def __init__(self, name: str, members: list[str] | None = None):
        self.name = name
        self.members = list(members or [])
        self.expenses: list[Expense] = []

    def add_member(self, name: str) -> str:
        """Add a person. Surrounding spaces are removed: " Ali " becomes "Ali"."""
        name = name.strip()
        if not name:
            raise ValueError("name cannot be empty")
        if name in self.members:
            raise ValueError(f"{name} is already in {self.name}")
        self.members.append(name)
        return name

    def add_expense(
        self,
        description: str,
        payer: str,
        amount: str,
        participants: list[str] | None = None,
    ) -> Expense:
        """Record that `payer` paid `amount` (like "12.50") for `participants`.

        Without participants, the expense is split between all members.
        """
        if participants is None:
            participants = list(self.members)
        if not participants:
            raise ValueError("an expense needs at least one participant")
        for person in [payer, *participants]:
            if person not in self.members:
                raise ValueError(f"{person} is not in {self.name}")
        expense = Expense(description, payer, to_cents(amount), participants)
        self.expenses.append(expense)
        return expense
