#! /usr/bin/env bash

if [ -f ./tests/.env.test ]; then
  set -a ; . ./tests/.env.test ; set +a
fi

# Let the DB start
python ./app/db/db_check.py

alembic upgrade head

# Create initial test data in DB
python ./tests/init_db.py