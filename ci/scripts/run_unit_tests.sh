#!/bin/bash
SQLITE_DB_FILE="$(pwd)/tests/data/test_data.db"
pytest -v tests/*_test.py  --junitxml=test-reports/report.xml

# Getting the total test count and generate a badge based on that (the color will always be blue)
UNIT_TEST_COUNT=$(xmlstarlet sel -t -v '//testsuite/@tests' test-reports/report.xml)
echo "Found ${UNIT_TEST_COUNT} unit tests"
python -m pybadges --left-text="unit tests" --right-text=$UNIT_TEST_COUNT --right-color='blue' > unit_test_count.svg

# Getting the pass rate calculating it based on the failed tests
calc(){ awk "BEGIN { print "$*" }"; }
UNIT_TEST_FAILED=$(xmlstarlet sel -t -v '//testsuite/@errors' test-reports/report.xml)
UNIT_TEST_PASSED=$(($UNIT_TEST_COUNT-$UNIT_TEST_FAILED))
PASS_RATE=$(calc $UNIT_TEST_PASSED/$UNIT_TEST_COUNT*100)

if [ "$PASS_RATE" -eq "100" ];
then
    python -m pybadges --left-text="pass rate" --right-text="${PASS_RATE}%" --right-color='green' > pass_rate.svg
else
    python -m pybadges --left-text="pass rate" --right-text="${PASS_RATE}%" --right-color='red' > pass_rate.svg
fi

exit $UNIT_TEST_FAILED
