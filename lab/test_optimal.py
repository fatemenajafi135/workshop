import pytest

from splitter.optimal import fewest_transfers
from splitter.settle import Transfer, settle_up


def settles(balances, transfers):
    left = dict(balances)
    for t in transfers:
        assert t.amount > 0
        left[t.sender] += t.amount
        left[t.receiver] -= t.amount
    return all(balance == 0 for balance in left.values())


def test_nothing_to_settle():
    assert fewest_transfers({}) == []
    assert fewest_transfers({"Ali": 0, "Bea": 0}) == []


def test_one_debt():
    assert fewest_transfers({"Ali": 500, "Bea": -500}) == [Transfer("Bea", "Ali", 500)]


def test_beats_greedy():
    # Bea and Cleo can settle between themselves, so 3 transfers are enough.
    balances = {"Ali": 400, "Bea": 300, "Cleo": -300, "Dan": -200, "Eve": -200}
    transfers = fewest_transfers(balances)
    assert settles(balances, transfers)
    assert len(transfers) == 3
    assert len(settle_up(balances)) == 4


@pytest.mark.parametrize(
    "balances, fewest",
    [
        ({"a": 500, "b": -200, "c": -300, "d": 700, "e": -700}, 3),
        ({"a": 100, "b": 200, "c": 300, "d": -600}, 3),
        ({"a": 1500, "b": -500, "c": -1000, "d": 800, "e": -300, "f": -500, "g": 50, "h": -50}, 5),
    ],
)
def test_known_answers(balances, fewest):
    transfers = fewest_transfers(balances)
    assert settles(balances, transfers)
    assert len(transfers) == fewest


def test_balances_that_do_not_add_up_raise():
    with pytest.raises(ValueError):
        fewest_transfers({"Ali": 500, "Bea": -400})
