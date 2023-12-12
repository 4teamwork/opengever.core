# httpd

Reverse proxy, responsible for dispatching requests to the appropriate service.

## Environment Variables

### `SERVER_ADMIN`

Email address that appears on some server-generated pages, such as error documents.

Default: admin@4teamwork.ch

### `SERVER_NAME`

The name and port that the server uses to identify itself.

Default: httpd:80

### `HTTP_PROTOCOL`

URL scheme used in backend generated URLs.

Default: https

### `HTTP_PORT`

Port used in backend generated URLs.

Default: 443

### `BACKEND_ID`

The site id of the backend.

Default: ogsite

### `BACKEND_PREFIX`

A path prefix used for backend generated URLs.

Default: /

### `BACKEND_HOST`

The name and port of the backend server.

Default: ogcore:8080

### `FRONTEND_HOST`

The name and port of the frontend server.

Default: ogui:80

### `BUMBLEBEE_HOST`

The name and port of the bumblebee server.

Default: bumblebee:80

### `BUMBLEBEE_PROTOCOL`

URL scheme used for bumblebee backend.

Default: http

### `PORTAL_HOST`

The name and port of the portal server.

Default: portal-frontend:80

### `SKIP_HTTPD_CONF`

If defined, generating httpd.conf is skipped at all. Instead a custom httpd.conf
can be bind mounted into the container.
