#!/bin/bash
set -euo pipefail

SQL_DB_NAME="zugogds"

rm -rf var/blobstorage_initial
rm -rf var/filestorage_initial

cp -r var/blobstorage var/blobstorage_initial
cp -r var/filestorage var/filestorage_initial

pg_dump -C $SQL_DB_NAME > var/ogds_${SQL_DB_NAME}_initial.sql
