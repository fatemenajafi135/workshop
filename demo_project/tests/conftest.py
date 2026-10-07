import pytest

from splitter.group import Group


@pytest.fixture
def trip() -> Group:
    """Three friends in Lisbon. Ali paid the hotel, Bea paid a dinner Ali skipped."""
    group = Group("Lisbon trip", members=["Ali", "Bea", "Cleo"])
    group.add_expense("Hotel", payer="Ali", amount="90.00")
    group.add_expense("Dinner", payer="Bea", amount="30.00", participants=["Bea", "Cleo"])
    return group
