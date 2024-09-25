#! /usr/bin/env bash

# Let the DB start
python ./app/db/db_check.py

# Create initial data in DB
python ./app/db/init_bible.py