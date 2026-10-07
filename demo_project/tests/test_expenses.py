import pytest

from splitter.expenses import split_equal


def test_split_evenly():
    assert split_equal(900, 3) == [300, 300, 300]


def test_leftover_cents_go_to_the_first_shares():
    assert split_equal(1000, 3) == [334, 333, 333]
    assert split_equal(1001, 3) == [334, 334, 333]


def test_shares_always_add_up_to_the_amount():
    for amount in range(0, 250):
        for n in range(1, 7):
            assert sum(split_equal(amount, n)) == amount


def test_split_between_nobody_raises():
    with pytest.raises(ValueError):
        split_equal(1000, 0)
