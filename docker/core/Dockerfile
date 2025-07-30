
# ogcore builder
# -----------------------------------------------------------------------------
FROM 4teamwork/plone:4.3.20-alpine3.20 AS builder
USER root

RUN apk add curl

RUN --mount=type=secret,id=gldt \
    export GITLAB_DEPLOY_TOKEN=$(cat /run/secrets/gldt) && \
    if [ $(uname -m) == "x86_64" ]; \
    then curl -v -O https://__token__:$GITLAB_DEPLOY_TOKEN@git.4teamwork.ch/api/v4/projects/492/packages/generic/openssl1.1-compat-dev/1.1.1w-r1/openssl1.1-compat-dev-1.1.1w-r1.apk; \
    else curl -v -O https://__token__:$GITLAB_DEPLOY_TOKEN@git.4teamwork.ch/api/v4/projects/493/packages/generic/openssl1.1-compat-dev/1.1.1w-r1/openssl1.1-compat-dev-1.1.1w-r1.apk; \
    fi && \
    apk add --allow-untrusted openssl1.1-compat-dev-1.1.1w-r1.apk && \
    rm openssl1.1-compat-dev-1.1.1w-r1.apk

RUN apk add \
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
    libpq \
    libpq-dev \
    gettext

# Fix support for python-ldap<3.4.2 with OpenLDAP 2.6
RUN echo "INPUT ( libldap.so )" > /usr/lib/libldap_r.so

WORKDIR /app

ENV PATH="/app/bin:$PATH"

COPY ./docker/core/requirements-core.txt ./docker/core/requirements-deployment.txt /app/
RUN --mount=type=cache,target=/root/.cache \
    --mount=type=secret,id=gldt \
    export GITLAB_DEPLOY_TOKEN=$(cat /run/secrets/gldt) && \
    CFLAGS="-I/usr/include/openssl1.1" \
    LDFLAGS="-L/usr/lib/openssl1.1" \
    pip install \
    --prefix /app \
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
    --prefix /app \
    --extra-index-url https://__token__:$GITLAB_DEPLOY_TOKEN@git.4teamwork.ch/api/v4/projects/486/packages/pypi/simple \
    -e . \
    -e /app/src/opengever.maintenance \
    -c requirements-core.txt \
    -c requirements-deployment.txt

RUN find /app/opengever -name "*.po" | xargs -I@ sh -c 'msgfmt @ -o "$(dirname @)/$(basename @ .po)".mo' && \
    find /app/plonetheme -name "*.po" | xargs -I@ sh -c 'msgfmt @ -o "$(dirname @)/$(basename @ .po)".mo'

# Plone needs permissions to update bundle schemas on import
RUN chown -R plone:plone /app/opengever/bundle/schemas

COPY ./docker/core/etc /app/etc
RUN chown -R plone:plone /app/etc
COPY ./docker/core/entrypoint.d /app/entrypoint.d
COPY ./docker/core/docker-entrypoint.sh ./docker/core/inituser /app/
COPY ./docker/core/zopectl /app/bin/
COPY --chown=plone ./docker/core/cron /app/cron
RUN chmod 644 /app/cron/crontab

RUN mkdir -p /app/var/log /app/var/instance \
 && chown plone:plone /app/var/log \
 && chown plone:plone /app/var/instance \
 && ln -sf /dev/stderr /app/var/log/instance.log \
 && ln -sf /dev/stdout /app/var/log/instance-json.log \
 && ln -sf /dev/stdout /app/var/log/solr-maintenance.log \
 && ln -sf /data/log/contentstats-json.log /app/var/log/contentstats-json.log \
 && ln -sf /data/log/nightly-jobs.log /app/var/log/nightly-jobs.log \
 && ln -sf /data/log/ogds-update.log /app/var/log/ogds-update.log

RUN ln -sf /dev/null /app/var/log/upgrade_stats.csv

# Patch cacert.pem with a recent version to address CVE-2023-37920
RUN wget -O /app/lib/python2.7/site-packages/certifi/cacert.pem https://raw.githubusercontent.com/certifi/python-certifi/2024.02.02/certifi/cacert.pem

# Patch ftw.bumblebee to use time.time() for timestamp generation
# datetime.now().strftime('%s') does not return the same on Alpine Linux (musl)
# https://www.openwall.com/lists/musl/2018/01/18/3
COPY ./docker/core/patches/hashing.py /app/lib/python2.7/site-packages/ftw/bumblebee/hashing.py
RUN python2.7 -m compileall /app/lib/python2.7/site-packages/ftw/bumblebee/hashing.py

# Patch p.a.theming to parse HTML with utf-8 encoding. By default the encoding is detected automatically.
# This no longer works reliably since upgrading to Alpine 3.20, therefore we set the encoding manually
# to utf-8 which should be fine for us.
COPY ./docker/core/patches/p_a_theming_transform.py /app/lib/python2.7/site-packages/plone/app/theming/transform.py
RUN python2.7 -m compileall /app/lib/python2.7/site-packages/plone/app/theming/transform.py

# go-crond builder
# -----------------------------------------------------------------------------
FROM golang:1.23-alpine3.20 AS go-crond-builder

RUN apk upgrade --no-cache --force
RUN apk add --update build-base make git

RUN mkdir -p /go/src/github.com/webdevops \
 && cd /go/src/github.com/webdevops \
 && git clone https://github.com/webdevops/go-crond.git

WORKDIR /go/src/github.com/webdevops/go-crond

ARG GOCROND_VERSION=23.12.0

RUN git checkout $GOCROND_VERSION
RUN go mod download
RUN make test
RUN make build

# ogcore production image
# -----------------------------------------------------------------------------
FROM 4teamwork/plone:4.3.20-alpine3.20 AS prod

USER root
RUN apk add \
    libldap \
    libffi \
    libpq \
    procps-ng

COPY --from=builder /app /app
COPY --from=go-crond-builder /go/src/github.com/webdevops/go-crond /usr/local/bin

VOLUME /data
WORKDIR /app
ENV PATH="/app/bin:$PATH"
USER plone
EXPOSE 8160
