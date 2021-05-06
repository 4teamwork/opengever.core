FROM 4teamwork/plone:4.3.20 AS build-stage

USER root

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libc-dev \
    zlib-dev \
    libjpeg-turbo-dev \
    libpng-dev \
    libxml2-dev \
    libxslt-dev \
    openldap-dev \
    libffi-dev \
    postgresql-dev \
    gettext

WORKDIR /app

ENV VIRTUAL_ENV=/app
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY ./docker/core/requirements-core.txt ./docker/core/requirements-deployment.txt /app/
RUN --mount=type=cache,target=/root/.cache \
    pip install \
    --extra-index-url https://buildout:buildout@psc.4teamwork.ch/simple \
    -r requirements-core.txt \
    -r requirements-deployment.txt

COPY setup.py README.rst HISTORY.rst ./
COPY ./opengever ./opengever
COPY ./plonetheme ./plonetheme
COPY ./src ./src

RUN --mount=type=cache,target=/root/.cache \
    pip install \
    --extra-index-url https://buildout:buildout@psc.4teamwork.ch/simple \
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


FROM 4teamwork/plone:4.3.20

USER root
RUN apk add --no-cache \
    libldap \
    libffi \
    libpq \
    tzdata \
 && ln -fs /usr/share/zoneinfo/Europe/Zurich /etc/localtime

COPY --from=build-stage /app /app

VOLUME /data
WORKDIR /app
ENV PATH="/app/bin:$PATH"
USER plone
EXPOSE 8160
