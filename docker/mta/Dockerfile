FROM alpine:3.21

RUN apk add --no-cache \
    postfix \
    python3 \
    py3-jinja2

COPY docker/mta/conf /etc/postfix
COPY docker/mta/configure-postfix.py docker/mta/mta2plone.py docker/mta/docker-entrypoint.sh /usr/local/bin/

VOLUME ["/var/spool/postfix"]

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

EXPOSE 25
