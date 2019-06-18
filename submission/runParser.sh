#!/usr/bin/env bash

echo -e "**NOTE: This parser requires Python 3\n"

printf 'Setup 1 of 4: \n\tEnter the directory containing Items json files: '
read -e -r json_filepath
echo -e "Setup 2 of 4: \n\tEnter the directory where you will save the dat files:"
echo -e "\t(or hit ENTER to save in current directory)"
read -e -r dat_filepath

if ["$dat_filepath" == '']
then
    dat_filepath="${PWD}/dat"
    mkdir ${dat_filepath} 2>/dev/null
fi

python3 ./parser.py ${json_filepath} ${dat_filepath} & pid=$!

while kill -0 ${pid} 2>/dev/null
do
    for c in / - \\ \|; do
        printf '%s\b' "$c";
        sleep 1;
    done;
done

echo -e "Setup 3 of 4: \n\tCreating SQLite tables in ebay_db and importing dat files..."
sqlite3 ./ebay_db < commands.sql

sqlite3 ./ebay_db <<END_SQL
.import ${dat_filepath}/categories.dat category
.import ${dat_filepath}/countries.dat country
.import ${dat_filepath}/locations.dat location
.import ${dat_filepath}/users.dat user
.import ${dat_filepath}/bids.dat bid
.import ${dat_filepath}/auctions.dat auction
.import ${dat_filepath}/join_auction_category.dat join_auction_category
END_SQL

echo -e "Setup 4 of 4: \n\tNormalizing database relationships..."

sqlite3 ./ebay_db < normalize.sql

echo -e "Parsing, ingesting, and normalizing complete. Testing queries..."