# Summary crashes after splitting €10 three ways

Ali paid €10.00 for a taxi for the three of us. Since then, opening the
summary crashes with:

    ValueError: balances must add up to zero

The balances look almost right: Ali is owed €6.67, Bea and Cleo owe €3.33
each. But €3.33 + €3.33 is €6.66, so a cent went missing somewhere.
