#!/bin/bash

COVERAGE_PERC=$(coverage report|tail -1|awk -F " " '{print $4}'|rev|cut -c2-|rev)
echo "COVERAGE_PERC=${COVERAGE_PERC}"
echo "GREEN_COVERAGE_THRESHOLD=${GREEN_COVERAGE_THRESHOLD}"
echo "YELLOW_COVERAGE_THRESHOLD=${YELLOW_COVERAGE_THRESHOLD}"

if [ "$COVERAGE_PERC" -ge "$GREEN_COVERAGE_THRESHOLD" ]; 
then 
	echo "Green coverage threshold met"; 
	python -m pybadges --left-text="coverage" --right-text="${COVERAGE_PERC}%" --right-color='green' > code_coverage.svg
	exit 0
elif [ "$COVERAGE_PERC" -ge "$YELLOW_COVERAGE_THRESHOLD" ];
then
	echo "Orange coverage threshold met"; 
	python -m pybadges --left-text="coverage" --right-text="${COVERAGE_PERC}%" --right-color='orange' > code_coverage.svg
	exit 0
else
	echo "Minimum coverage threshold not met";
	python -m pybadges --left-text="coverage" --right-text="${COVERAGE_PERC}%" --right-color='red' > code_coverage.svg
	exit 1
fi

