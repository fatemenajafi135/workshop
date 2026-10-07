#!/bin/sh
# Maintainer check, not for attendees. For every bug:
#   1. planted: the failing tests are exactly the ones in its test.txt
#   2. undone:  reversing the patch makes the whole suite green again
cd "$(dirname "$0")/.."
CONTAINER=mini-agent-verify
problems=0

failing_tests() {
    docker exec $CONTAINER python -m pytest -q --tb=no -rfE 2>&1 \
        | grep -E '^(FAILED|ERROR) ' \
        | sed -E 's/^(FAILED|ERROR) //; s/ - .*//' \
        | LC_ALL=C sort
}

for dir in bugs/*/; do
    bug=$(basename "$dir")
    make -s reset BUG="${bug%%-*}" CONTAINER=$CONTAINER > /dev/null || exit 1

    if ! failing_tests | diff -u "$dir/test.txt" - > /dev/null; then
        echo "FAIL $bug: failing tests differ from test.txt:"
        failing_tests | diff -u "$dir/test.txt" -
        problems=1
        continue
    fi

    docker exec -i $CONTAINER git apply -R < "$dir/bug.patch"
    if [ -n "$(failing_tests)" ]; then
        echo "FAIL $bug: suite is not green after undoing the patch"
        problems=1
        continue
    fi

    echo "ok   $bug ($(wc -l < "$dir/test.txt") failing tests)"
done

docker rm -f $CONTAINER > /dev/null
exit $problems
