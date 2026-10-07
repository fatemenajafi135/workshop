from splitter.balances import balances
from splitter.group import Group


def test_trip_balances(trip):
    assert balances(trip) == {"Ali": 6000, "Bea": -1500, "Cleo": -4500}


def test_new_group_balances_are_zero():
    group = Group("Weekend", members=["Ali", "Bea"])
    assert balances(group) == {"Ali": 0, "Bea": 0}


def test_person_who_was_not_there_pays_nothing():
    group = Group("Weekend", members=["Ali", "Bea", "Cleo"])
    group.add_expense("Cinema", payer="Bea", amount="20.00", participants=["Bea", "Cleo"])
    assert balances(group)["Ali"] == 0


def test_leftover_cent_goes_to_first_participant():
    group = Group("Weekend", members=["Ali", "Bea", "Cleo"])
    group.add_expense("Taxi", payer="Ali", amount="10.00", participants=["Cleo", "Bea", "Ali"])
    assert balances(group) == {"Ali": 667, "Bea": -333, "Cleo": -334}


def test_balances_add_up_to_zero():
    group = Group("Weekend", members=["Ali", "Bea", "Cleo", "Dan"])
    group.add_expense("Groceries", payer="Ali", amount="47.11")
    group.add_expense("Taxi", payer="Bea", amount="10.00", participants=["Ali", "Bea", "Cleo"])
    group.add_expense("Coffee", payer="Dan", amount="7.01", participants=["Cleo", "Dan"])
    assert sum(balances(group).values()) == 0
