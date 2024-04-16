#! /bin/sh

echo "opengever.core" $(grep '^version =' setup.py)

export GEVER_READ_ONLY_MODE="true"
export FTW_STRUCTLOG_MUTE_SETUP_ERRORS="true"
export PYTHONUNBUFFERED="1"
export ZSERVER_PORT="55001"
export LISTENER_HOST="0.0.0.0"
export LISTENER_PORT="55002"

exec "/app/bin/testserver" "-vv"
