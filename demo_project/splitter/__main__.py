"""Try the app: python -m splitter

Three short stories, the way a user would see the app.
Each one first shows what was entered (who paid what), then what the app says.
"""

from splitter.group import Group
from splitter.money import format_eur
from splitter.report import summary


def show(group: Group) -> None:
    print(f"{group.name}. Members: {', '.join(group.members)}")
    for expense in group.expenses:
        who = ", ".join(expense.participants)
        print(f"  {expense.payer} paid {format_eur(expense.amount)} for {expense.description} (shared by {who})")
    print()
    print(summary(group))


def lisbon_trip() -> None:
    trip = Group("Lisbon trip", members=["Ali", "Bea", "Cleo"])
    trip.add_expense("Hotel", payer="Ali", amount="90.00")
    trip.add_expense("Dinner (Ali stayed at the hotel)", payer="Bea", amount="30.00",
                     participants=["Bea", "Cleo"])
    trip.add_expense("Museum for Bea and Cleo", payer="Cleo", amount="24.10",
                     participants=["Bea", "Cleo"])
    show(trip)


def taxi_for_three() -> None:
    taxi = Group("Airport taxi", members=["Ali", "Bea", "Cleo"])
    taxi.add_expense("Taxi", payer="Ali", amount="10.00")
    show(taxi)


def two_new_groups() -> None:
    flat = Group("Flat")
    flat.add_member("Dana")
    flat.add_member("Eli")
    print("We made the group 'Flat' and added Dana and Eli.")
    ski = Group("Ski weekend")
    ski.add_member("Ali")
    ski.add_member("Bea")
    print("Then a new group, 'Ski weekend', and we added only Ali and Bea.\n")
    show(ski)


for story in [lisbon_trip, taxi_for_three, two_new_groups]:
    print(f"\n=== {story.__name__.replace('_', ' ')} ===\n")
    try:
        story()
    except Exception as error:
        print(f"CRASH: {type(error).__name__}: {error}")
