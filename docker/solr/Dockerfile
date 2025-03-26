FROM solr:9.8.1

ENV SOLR_OPTS="-Dlog4j2.formatMsgNoLookups=true"
ENV SOLR_CORES="ogsite"
ENV SOLR_MODULES=extraction,langid,analysis-extras,data-import-handler

USER root
RUN cd /opt/solr/modules \
 && mkdir -p data-import-handler/lib \
 && cd data-import-handler \
 && curl -OL https://raw.githubusercontent.com/SearchScale/dataimporthandler/refs/heads/master/README.md \
 && cd lib \
 && curl -OL https://github.com/SearchScale/dataimporthandler/releases/download/v9.7.0/data-import-handler-9.7.0.jar
USER solr

COPY ./solr-conf /opt/solr/server/solr/configsets/ogsite
COPY ./docker/solr/create_and_update_cores.sh /docker-entrypoint-initdb.d/create_and_update_cores.sh
