FROM httpd:2.4-alpine

RUN apk add --no-cache esh curl

COPY ./docker/httpd/conf/httpd.conf.esh /usr/local/apache2/conf/httpd.conf.esh
COPY ./docker/httpd//msoffice.html /usr/local/apache2/htdocs/msoffice.html
COPY ./docker/httpd/httpd-foreground /usr/local/bin/
