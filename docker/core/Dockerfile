FROM 4teamwork/plone:4.3.20 AS build-stage

USER root

RUN apk add --virtual .build-deps \
    gcc \
    musl-dev \
    libc-dev \
    zlib-dev \
    libjpeg-turbo-dev \
    libpng-dev \
    libxml2-dev \
    libxslt-dev \
    python2-dev \
    openldap-dev \
    libffi-dev \
    postgresql-dev \
    gettext

WORKDIR /app

ENV VIRTUAL_ENV=/app
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY ./docker/core/requirements-core.txt ./docker/core/requirements-deployment.txt /app/
RUN --mount=type=cache,target=/root/.cache \
    --mount=type=secret,id=gldt \
    export GITLAB_DEPLOY_TOKEN=$(cat /run/secrets/gldt) && \
    pip install \
    --extra-index-url https://__token__:$GITLAB_DEPLOY_TOKEN@git.4teamwork.ch/api/v4/projects/486/packages/pypi/simple \
    -r requirements-core.txt \
    -r requirements-deployment.txt

COPY setup.py README.rst HISTORY.rst ./
COPY ./opengever ./opengever
COPY ./plonetheme ./plonetheme
COPY ./src ./src

RUN --mount=type=cache,target=/root/.cache \
    --mount=type=secret,id=gldt \
    export GITLAB_DEPLOY_TOKEN=$(cat /run/secrets/gldt) && \
    pip install \
    --extra-index-url https://__token__:$GITLAB_DEPLOY_TOKEN@git.4teamwork.ch/api/v4/projects/486/packages/pypi/simple \
    -e /app/src/collective.js.timeago \
    -e . \
    -e /app/src/opengever.maintenance \
    -c requirements-core.txt \
    -c requirements-deployment.txt

RUN find /app/opengever -name "*.po" | xargs -I@ sh -c 'msgfmt @ -o "$(dirname @)/$(basename @ .po)".mo' && \
    find /app/plonetheme -name "*.po" | xargs -I@ sh -c 'msgfmt @ -o "$(dirname @)/$(basename @ .po)".mo'

COPY ./docker/core/etc /app/etc
RUN chown -R plone:plone /app/etc
COPY ./docker/core/entrypoint.d /app/entrypoint.d
COPY ./docker/core/docker-entrypoint.sh ./docker/core/inituser /app/

RUN mkdir -p /app/var/log \
 && ln -sf /dev/stderr /app/var/log/instance.log \
 && ln -sf /dev/stdout /app/var/log/instance-json.log \
 && ln -sf /dev/stdout /app/var/log/solr-maintenance.log

RUN ln -sf /dev/null /app/var/log/upgrade_stats.csv

# Patch ftw.bumblebee to use time.time() for timestamp generation
# datetime.now().strftime('%s') does not return the same on Alpine Linux (musl)
# https://www.openwall.com/lists/musl/2018/01/18/3
COPY ./docker/core/patches/hashing.py /app/lib/python2.7/site-packages/ftw/bumblebee/hashing.py
RUN python2.7 -m compileall /app/lib/python2.7/site-packages/ftw/bumblebee/hashing.py

COPY ./docker/core/patches/z3c_autoinclude_utils.py /app/lib/python2.7/site-packages/z3c/autoinclude/utils.py
RUN python2.7 -m compileall /app/lib/python2.7/site-packages/z3c/autoinclude/utils.py

FROM 4teamwork/plone:4.3.20

USER root
RUN apk add \
    libldap \
    libffi \
    libpq

COPY --from=build-stage /app /app

VOLUME /data
WORKDIR /app
ENV PATH="/app/bin:$PATH"
USER plone
EXPOSE 8160
