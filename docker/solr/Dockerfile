FROM solr:9.8.1

ENV SOLR_OPTS="-Dlog4j2.formatMsgNoLookups=true" \
    SOLR_CORES="ogsite" \
    SOLR_MODULES=extraction,langid,analysis-extras,data-import-handler,scripting \
    SOLR_SECURITY_MANAGER_ENABLED=false

USER root

# Add Data Import Handler as Solr module
RUN cd /opt/solr/modules \
 && mkdir -p data-import-handler/lib \
 && cd data-import-handler \
 && curl -OL https://raw.githubusercontent.com/SearchScale/dataimporthandler/refs/heads/master/README.md \
 && cd lib \
 && curl -OL https://github.com/SearchScale/dataimporthandler/releases/download/v9.7.0/data-import-handler-9.7.0.jar \
# Add Nashorn JS Engine for ScriptUpdateProcessorFactory
 && cd /opt/solr/lib \
 && curl -OL https://repo1.maven.org/maven2/org/openjdk/nashorn/nashorn-core/15.6/nashorn-core-15.6.jar \
 && curl -OL https://repo1.maven.org/maven2/org/ow2/asm/asm-commons/7.3.1/asm-commons-7.3.1.jar \
 && curl -OL https://repo1.maven.org/maven2/org/ow2/asm/asm-tree/7.3.1/asm-tree-7.3.1.jar \
 && curl -OL https://repo1.maven.org/maven2/org/ow2/asm/asm-util/7.3.1/asm-util-7.3.1.jar \
 && curl -OL https://repo1.maven.org/maven2/org/ow2/asm/asm/7.3.1/asm-7.3.1.jar \
 && curl -OL https://repo1.maven.org/maven2/org/ow2/asm/asm-analysis/7.3.1/asm-analysis-7.3.1.jar

USER solr

COPY ./solr-conf /opt/solr/server/solr/configsets/ogsite
COPY ./docker/solr/create_and_update_cores.sh /docker-entrypoint-initdb.d/create_and_update_cores.sh
