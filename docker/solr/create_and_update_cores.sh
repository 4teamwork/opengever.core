#!/bin/bash
set -e

CONFIG_SOURCE=/opt/solr/server/solr/configsets/ogsite
CORES_DIR=/var/solr/data

# If ZK_HOST is defined, then assume SolrCloud mode
if [ -z ${ZK_HOST} ]; then
	for core in ${SOLR_CORES}; do
		coredir="$CORES_DIR/$core"
		if [ ! -d "$coredir" ]; then
			mkdir -p "$coredir/conf"
			echo "name=$core" >"$coredir/core.properties"
			cp -r "$CONFIG_SOURCE/"* "$coredir/conf/"
		else
			cp -r "$CONFIG_SOURCE/"* "$coredir/conf/"
		fi
	done
fi
