#! /usr/bin/env bash

# Let the DB start
python ./app/db/db_check.py

alembic upgrade head

# Create initial data in DB
python ./app/db/start/init_db.py