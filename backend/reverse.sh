#! /usr/bin/env bash

read -e -p "Enter bible version to export (or all to export all versions) : " -i "all" VERSION
# Reverse data
python ./app/db/export_version.py "$VERSION"