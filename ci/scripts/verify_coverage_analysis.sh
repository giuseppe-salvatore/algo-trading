#!/bin/bash

COVERAGE_PERC=$(coverage report|tail -1|awk -F " " '{print $4}'|rev|cut -c2-|rev)

if [ "$COV_PERC" -le "$MIN_COVERAGE_THRESHOLD" ]; 
then 
	echo "Coverage threshold not met"; 
	exit 1
else 
	echo "Coverage threshold met"; 
	exit 0
fi

