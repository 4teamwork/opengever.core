#!/bin/bash
set -euo pipefail

SQL_DB_NAME="zugogds"

rm -rf var/blobstorage
rm -rf var/filestorage

cp -r var/blobstorage_initial var/blobstorage
cp -r var/filestorage_initial var/filestorage

dropdb $SQL_DB_NAME
createdb $SQL_DB_NAME
psql $SQL_DB_NAME < var/ogds_${SQL_DB_NAME}_initial.sql
