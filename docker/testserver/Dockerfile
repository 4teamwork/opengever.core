FROM 4teamwork/ogcore:latest

USER root
WORKDIR /app

COPY ./docker/testserver/requirements-testserver.txt /app/
RUN --mount=type=cache,target=/root/.cache \
    pip install \
    --extra-index-url https://buildout:buildout@psc.4teamwork.ch/simple \
    -r requirements-testserver.txt \
    -c requirements-core.txt \
    -c requirements-deployment.txt

HEALTHCHECK --start-period=2m CMD /app/bin/testserverctl connectiontest
COPY ./bin/testserverctl ./docker/testserver/bin/testserver /app/bin
COPY ./docker/testserver/docker-entrypoint.sh /app/

USER plone
EXPOSE 55001
EXPOSE 55002
