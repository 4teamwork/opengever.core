FROM 4teamwork/ogcore:latest

USER root
WORKDIR /app

COPY ./docker/testserver/requirements-testserver.txt /app/
RUN --mount=type=cache,target=/root/.cache \
    --mount=type=secret,id=gldt \
    export GITLAB_DEPLOY_TOKEN=$(cat /run/secrets/gldt) && \
    pip install \
    --extra-index-url https://__token__:$GITLAB_DEPLOY_TOKEN@git.4teamwork.ch/api/v4/projects/486/packages/pypi/simple \
    -r requirements-testserver.txt \
    -c requirements-core.txt \
    -c requirements-deployment.txt

HEALTHCHECK --start-period=2m CMD /app/bin/testserverctl connectiontest
COPY ./bin/testserverctl ./docker/testserver/bin/testserver /app/bin/
COPY ./docker/testserver/docker-entrypoint.sh /app/

ENV SOLR_HOSTNAME=testserver-solr
ENV TESTSERVER_REUSE_RUNNING_SOLR=8983
ENV SOLR_PORT=8983
ENV MSGCONVERT_URL=http://msgconvert:8080/
ENV SABLON_URL=http://sablon:8080/
ENV PDFLATEX_URL=http://pdflatex:8080/
ENV WEASYPRINT_URL=http://weasyprint:8080/

USER plone
EXPOSE 55001
EXPOSE 55002
