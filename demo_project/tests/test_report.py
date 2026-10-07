from splitter.group import Group
from splitter.report import summary


def test_trip_summary(trip):
    assert summary(trip) == (
        "Lisbon trip\n"
        "\n"
        "Ali is owed €60.00\n"
        "Bea owes €15.00\n"
        "Cleo owes €45.00\n"
        "\n"
        "To settle up:\n"
        "  Cleo pays Ali €45.00\n"
        "  Bea pays Ali €15.00"
    )


def test_summary_of_group_without_expenses():
    group = Group("Weekend", members=["Ali", "Bea"])
    assert summary(group) == (
        "Weekend\n"
        "\n"
        "Ali is settled up\n"
        "Bea is settled up\n"
        "\n"
        "To settle up:\n"
        "  nothing to do"
    )
