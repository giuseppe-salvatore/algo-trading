#!/bin/bash
DATE=`date +"%Y-%m-%d"`
DEST_HOST="dark-matter.local"
DEST_ROOT_LOCATION="~/workspace/personal/algo-trading"

echo "Copy alpaca SQL scripts"
scp ./data/alpaca/sql/*.sql "${DEST_HOST}":"${DEST_ROOT_LOCATION}/data/alpaca/sql/"

echo "Copy alphavantage SQL scripts"
scp -r ./data/alphavantage/sql "${DEST_HOST}:${DEST_ROOT_LOCATION}/data/alphavantage/sql/"

echo "Backing up existing DBs"
ssh ${DEST_HOST} -t "cp ${DEST_ROOT_LOCATION}/data/stock_data.alpaca.db ${DEST_ROOT_LOCATION}/data/stock_data.alpaca.${DATE}.db"
ssh ${DEST_HOST} -t "cp ${DEST_ROOT_LOCATION}/data/stock_data.alphavantage.db ${DEST_ROOT_LOCATION}/data/stock_data.alphavantage.${DATE}.db"

echo "Copy DBs"
scp "./data/stock_data.alpaca.db" "${DEST_HOST}:${DEST_ROOT_LOCATION}/data/stock_data.alpaca.db"
scp "./data/stock_data.alphavantage.db" "${DEST_HOST}:${DEST_ROOT_LOCATION}/data/stock_data.alphavantage.db"
