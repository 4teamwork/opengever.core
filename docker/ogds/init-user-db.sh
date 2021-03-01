#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER ogds PASSWORD 'secret';
    CREATE DATABASE ogds WITH OWNER ogds;
EOSQL
