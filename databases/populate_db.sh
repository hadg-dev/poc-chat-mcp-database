#!/bin/bash
# from repo root (where database.db lives)
curl -L -o Chinook_Sqlite.sql \
  https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql

# rebuild (or build) your DB from the script
rm -f database.db
sqlite3 database.db < Chinook_Sqlite.sql

# quick sanity check
sqlite3 database.db ".tables"
sqlite3 database.db "SELECT name, COUNT(*) FROM sqlite_master WHERE type='table' GROUP BY 1;"

# point the server explicitly (belt-and-suspenders)
export SQLITE_DB_PATH="$PWD/database.db"