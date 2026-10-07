import pytest

from splitter.balances import balances
from splitter.settle import Transfer, settle_up


def test_nothing_to_settle_without_balances():
    assert settle_up({}) == []


def test_nothing_to_settle_when_everyone_is_even():
    assert settle_up({"Ali": 0, "Bea": 0}) == []


def test_one_debt():
    assert settle_up({"Ali": 500, "Bea": -500}) == [Transfer("Bea", "Ali", 500)]


def test_trip_settles(trip):
    assert settle_up(balances(trip)) == [
        Transfer("Cleo", "Ali", 4500),
        Transfer("Bea", "Ali", 1500),
    ]


def test_everyone_ends_at_zero():
    start = {"Ali": 2500, "Bea": -1000, "Cleo": 700, "Dan": -1999, "Eve": -201}
    end = dict(start)
    for t in settle_up(start):
        end[t.sender] += t.amount
        end[t.receiver] -= t.amount
    assert all(balance == 0 for balance in end.values())


def test_balances_that_do_not_add_up_raise():
    with pytest.raises(ValueError):
        settle_up({"Ali": 500, "Bea": -400})
