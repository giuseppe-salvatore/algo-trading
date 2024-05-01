#!/bin/bash

pwd

DATE=`date +"%Y-%m-%d"`

echo "Updating current month on ${DATE} for previous month"

MAIN_DB_FILE="data/stock_data.alpaca.db"
TARGET_BACKUP_FILE="data/stock_data.alpaca.${DATE}.db"
if [ -f $TARGET_BACKUP_FILE ];
then 
    echo "File already exists, skipping backup"
else
    echo "Backup into file ${TARGET_BACKUP_FILE}"
    cp "${MAIN_DB_FILE}" "${TARGET_BACKUP_FILE}"
fi


make pull-alpaca

make store-alpaca

make db-info-alpaca > "data/stock_data.alpaca.db.${DATE}.info"

echo "All done, now cleaning up the database "${MAIN_DB_FILE}""
echo "vacuum;" | sqlite3 "${MAIN_DB_FILE}"