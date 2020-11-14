#!/bin/bash
#SQLITE_DB_FILE="$(pwd)/tests/data/test_data.db"
REPORT_FILE="test-reports/bdd_report.xml"
python -m pytest -v bdd/ --junitxml=${REPORT_FILE}

# Getting the total test count and generate a badge based on that (the color will always be blue)

TEST_COUNT=$(xmlstarlet sel -t -v '//testsuite/@tests' ${REPORT_FILE})
TEST_FAILED=$(xmlstarlet sel -t -v '//testsuite/@failures' ${REPORT_FILE})
TEST_ERRORS=$(xmlstarlet sel -t -v '//testsuite/@errors' ${REPORT_FILE})
echo "Found ${TEST_COUNT} bdd tests"

# Getting the pass rate calculating it based on the failed tests
calc(){ awk "BEGIN { print "$*" }"; }
TOTAL_ERRORS=$((${TEST_FAILED}+${TEST_ERRORS}))
TEST_PASSED=$((${TEST_COUNT}-${TOTAL_ERRORS}))
PASS_RATE=$(calc ${TEST_PASSED}/${TEST_COUNT}*100)

if [ "$PASS_RATE" -eq "100" ];
then
    python -m pybadges --left-text="BDD" --right-text="${PASS_RATE}%" --right-color='green' > bdd_pass_rate.svg
else
    python -m pybadges --left-text="BDD" --right-text="${PASS_RATE}%" --right-color='red' > bdd_pass_rate.svg
fi

exit $TOTAL_ERRORS