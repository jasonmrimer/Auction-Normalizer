#!/usr/bin/env bash

echo -e "**NOTE: This parser requires Python 3\n"

echo -e "Setup 1 of 5: \n\tEnter the directory containing Items json files"
printf "\t(navigate up using ../.. or use complete path but do NOT use ~/) > "
read -e -r json_filepath
echo -e "Setup 2 of 5: \n\tEnter the directory to save dat files"
printf "\t(or hit ENTER to save in current directory) > "
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

echo -e "Setup 3 of 5: \n\tCreating SQLite tables in ebay_db and importing dat files..."
sqlite3 ./ebay_db < create.sql

sqlite3 ./ebay_db <<END_SQL
.import ${dat_filepath}/categories.dat category
.import ${dat_filepath}/countries.dat country
.import ${dat_filepath}/locations.dat location
.import ${dat_filepath}/users.dat user
.import ${dat_filepath}/bids.dat bid
.import ${dat_filepath}/auctions.dat auction
.import ${dat_filepath}/join_auction_category.dat join_auction_category
END_SQL

echo -e "Setup 4 of 5: \n\tNormalizing database relationships..."

#sqlite3 ./ebay_db < normalize.sql

echo -e "Step 5: Testing queries...\n"
echo -e '1. Find the number of users in the database.'
echo -e "\tCorrect Answer > 13422 | $(sqlite3 ./ebay_db < query1.sql) < My Answer"
echo -e '2. Find the number of users from New York (i.e., users whose location is the string ”New York”).'
echo -e "\tCorrect Answer > 80 | $(sqlite3 ./ebay_db < query2.sql) < My Answer"
echo -e '3. Find the number of auctions belonging to exactly four categories.'
echo -e "\tCorrect Answer > 8365 | $(sqlite3 ./ebay_db < query3.sql) < My Answer"
echo -e '4. Find the ID(s) of auction(s) with the highest current price.'
echo -e "\tCorrect Answer > 1046871451 | $(sqlite3 ./ebay_db < query4.sql)* < My Answer"
echo -e '5. Find the number of sellers whose rating is higher than 1000.'
echo -e "\tCorrect Answer > 3130 | $(sqlite3 ./ebay_db < query5.sql) < My Answer"
echo -e '6. Find the number of users who are both sellers and bidders.'
echo -e "\tCorrect Answer > 6717 | $(sqlite3 ./ebay_db < query6.sql) < My Answer"
echo -e '7. Find the number of categories that include at least one item with a bid of more than $100.'
echo -e "\tCorrect Answer > 150 | $(sqlite3 ./ebay_db < query7.sql) < My Answer"
echo -e "\n*The given answer to #4 (1046871451) is an incorrect highest price due 1NF db."
echo -e "Through discussions with Professor Khalefa on June 14, this normalized answer is preferred."

echo -e "\n\nProgram complete. Student: Jason Rimer"
