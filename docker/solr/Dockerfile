FROM solr:8.11.4

ENV SOLR_OPTS="-Dlog4j2.formatMsgNoLookups=true"
ENV SOLR_CORES="ogsite"
COPY ./solr-conf /opt/solr/server/solr/configsets/ogsite
COPY ./docker/solr/create_and_update_cores.sh /docker-entrypoint-initdb.d/create_and_update_cores.sh
