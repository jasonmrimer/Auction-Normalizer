#!/usr/bin/env bash
echo -e "**NOTE: This parser requires Python 3\n"
printf 'Setup 1 of 3: \n\tEnter the directory containing Items json files: '
read -e -r json_filepath
echo -e "Setup 2 of 3: \n\tEnter the directory where you will save the dat files:"
echo -e "\t(or hit ENTER to save in current directory)"
read -e -r dat_filepath

if ["$dat_filepath" == '']
then
    dat_filepath="${PWD}/dat"
    mkdir ${dat_filepath} 2>/dev/null
fi

python3 ./IngestApp.py ${json_filepath} ${dat_filepath} & pid=$!

while kill -0 ${pid} 2>/dev/null
do
    for c in / - \\ \|; do
        printf '%s\b' "$c";
        sleep 1;
    done;
done