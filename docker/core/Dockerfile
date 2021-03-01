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
RUN pip install \
    --no-cache-dir \
    --extra-index-url https://buildout:buildout@psc.4teamwork.ch/simple \
    -r requirements-core.txt \
    -r requirements-deployment.txt

COPY setup.py README.rst ./
COPY ./docs/HISTORY.txt ./docs/HISTORY.txt
COPY ./opengever ./opengever
COPY ./plonetheme ./plonetheme
COPY ./src ./src

RUN pip install \
    --no-cache-dir \
    --extra-index-url https://buildout:buildout@psc.4teamwork.ch/simple \
    -e /app/src/collective.js.timeago \
    -e . \
    -e /app/src/opengever.maintenance \
    -c requirements-core.txt \
    -c requirements-deployment.txt

# RUN pip install \
#     -e /app/src/collective.js.timeago \
#     -e /app/src/opengever.maintenance \
#     -c versions.txt

COPY ./docker/core/etc /app/etc
COPY ./docker/core/create_zope_conf.py /app/

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


# RUN apk add tzdata gcc musl-dev postgresql-dev \
#  && ln -fs /usr/share/zoneinfo/Europe/Zurich /etc/localtime

# RUN /app/bin/pip install ftw.table[extjs] psycopg2 -c versions.txt

# RUN mkdir -p /data/filestorage /data/blobstorage
# # Currently ownership and permissions are not preserved when copying from
# # another stage. Should be fixed with Docker 19.03 or later
# # https://github.com/moby/moby/pull/38599
# RUN chown -R plone:plone /data /plone/var /plone/etc/zope.conf

# VOLUME /data
ENV PATH="/app/bin:$PATH"
USER plone
EXPOSE 8160
# WORKDIR /app

