import pytest

from splitter.group import Group


def test_add_member_strips_spaces():
    group = Group("Flat")
    assert group.add_member("  Ali ") == "Ali"
    assert group.members == ["Ali"]


def test_add_same_member_twice_raises():
    group = Group("Flat")
    group.add_member("Bea")
    with pytest.raises(ValueError):
        group.add_member("Bea")


def test_add_member_with_empty_name_raises():
    with pytest.raises(ValueError):
        Group("Flat").add_member("   ")


def test_new_group_has_no_members():
    assert Group("Weekend").members == []


def test_expense_amount_is_stored_in_cents(trip):
    assert trip.expenses[0].amount == 9000


def test_expense_is_split_between_everyone_by_default(trip):
    assert trip.expenses[0].participants == ["Ali", "Bea", "Cleo"]


def test_expense_with_unknown_payer_raises(trip):
    with pytest.raises(ValueError):
        trip.add_expense("Taxi", payer="Dan", amount="20.00")


def test_expense_with_unknown_participant_raises(trip):
    with pytest.raises(ValueError):
        trip.add_expense("Taxi", payer="Ali", amount="20.00", participants=["Ali", "Dan"])


def test_expense_without_participants_raises(trip):
    with pytest.raises(ValueError):
        trip.add_expense("Taxi", payer="Ali", amount="20.00", participants=[])
