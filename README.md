use IngestApp to create all dat files

use Terminal to import dat files:
sqlite3
.open ebay_db.db
.import 'filepath/file.dat' table_name

JSONParser runs anonymous parsing methods when passed JSON files

IngestJSON combines the extraction from many files and writes the results to a dat file 