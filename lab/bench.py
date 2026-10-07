"""The lab's benchmark. Piped into the sandbox when measuring, never stored there.

Input (argv[1]): JSON list of {"balances": {...}, "fewest": n}.
Output, last line: {"ok": true, "seconds": ...} or {"ok": false, "error": "..."}.
"""

import json
import sys
import time

from splitter.optimal import fewest_transfers

REPEATS = 3  # each group runs 3 times, the fastest run counts


def problem_with(balances: dict[str, int], transfers, fewest: int) -> str | None:
    left = dict(balances)
    for t in transfers:
        if not (isinstance(t.amount, int) and t.amount > 0):
            return f"transfer amount must be a positive int, got {t.amount!r}"
        if t.sender not in left or t.receiver not in left:
            return f"unknown person in {t}"
        left[t.sender] += t.amount
        left[t.receiver] -= t.amount
    if any(left.values()):
        return "the transfers don't settle everyone"
    if len(transfers) != fewest:
        return f"{len(transfers)} transfers, but {fewest} is possible"
    return None


def main() -> None:
    total = 0.0
    for case in json.loads(sys.argv[1]):
        fastest = float("inf")
        for repeat in range(REPEATS):
            # New names every time, so remembering earlier answers doesn't help.
            balances = {f"{name}.{repeat}": amount for name, amount in case["balances"].items()}
            start = time.perf_counter()
            transfers = fewest_transfers(dict(balances))
            fastest = min(fastest, time.perf_counter() - start)
            problem = problem_with(balances, transfers, case["fewest"])
            if problem:
                print(json.dumps({"ok": False, "error": problem}))
                return
        total += fastest
    print(json.dumps({"ok": True, "seconds": total}))


main()
