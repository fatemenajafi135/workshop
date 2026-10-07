"""Try the app: python -m splitter

Three short stories, the way a user would see the app.
"""

from splitter.group import Group
from splitter.report import summary


def lisbon_trip() -> None:
    trip = Group("Lisbon trip", members=["Ali", "Bea", "Cleo"])
    trip.add_expense("Hotel", payer="Ali", amount="90.00")
    trip.add_expense("Dinner, Ali stayed at the hotel", payer="Bea", amount="30.00",
                     participants=["Bea", "Cleo"])
    trip.add_expense("Museum for Bea and Cleo", payer="Cleo", amount="24.10",
                     participants=["Bea", "Cleo"])
    print(summary(trip))


def taxi_for_three() -> None:
    taxi = Group("Airport taxi", members=["Ali", "Bea", "Cleo"])
    taxi.add_expense("Taxi", payer="Ali", amount="10.00")
    print(summary(taxi))


def two_new_groups() -> None:
    flat = Group("Flat")
    flat.add_member("Dana")
    flat.add_member("Eli")
    ski = Group("Ski weekend")
    ski.add_member("Ali")
    ski.add_member("Bea")
    print(summary(ski))


for story in [lisbon_trip, taxi_for_three, two_new_groups]:
    print(f"\n=== {story.__name__.replace('_', ' ')} ===\n")
    try:
        story()
    except Exception as error:
        print(f"CRASH: {type(error).__name__}: {error}")
