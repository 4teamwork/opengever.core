#! /bin/sh
INSTANCE_HOME="/app"
CONFIG_FILE="/app/etc/zope.conf"
ZOPE_RUN="/app/bin/runzope"
ZOPE_CTL="/app/bin/zopectl"
export INSTANCE_HOME

mkdir -p /data/log

python /app/entrypoint.d/create_zope_conf.py "$CONFIG_FILE"
python /app/entrypoint.d/create_ogds_zcml.py
python /app/entrypoint.d/create_solr_zcml.py
python /app/entrypoint.d/create_package_includes.py
python /app/entrypoint.d/create_crontab.py

if [ $# -eq 0 ]
then
  exec "$ZOPE_RUN" -C "$CONFIG_FILE"
elif [ "$*" = "cron" ]
then
  exec go-crond -v --allow-unprivileged --server.bind=':8080' --server.metrics plone:/app/cron/crontab
else
  exec "$ZOPE_CTL" -C "$CONFIG_FILE" "$@"
fi
