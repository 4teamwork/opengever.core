# Running opengever.core with Docker

## Overview

The provided Docker Compose file contains a production like setup of
opengever.core consisting of various services:

- httpd (reverse proxy)
- ogui (frontend)
- ogcore (backend)
- zeoserver (ZODB storage server)
- ogds (PostgreSQL database)
- solr (Solr search engine)
- msgconvert (MSG to EML conversion service)
- sablon (Word document template processor service)
- pdflatex (PDFLaTeX service)
- weasyprint (HTML to PDF creation service)
- ianus-frontend (authentication portal frontend)
- ianus-backend (authentication portal backend)
- ianus-db (authentication portal database)

Optional services:

- clamav (virus scanning engine)
- ds389 (389 Directory Server)

## Configuration

Before running GEVER/teamraum with Docker you need to setup a few configuration
settings.

### Hostname

Currently the application cannot be served from a localhost URL. This is
because of communication between services as they need to connect to each other
by hostname and this hostname must point to the Docker host. Using localhost
would resolve to the Docker container.

Therefore add a hostname to `/etc/hosts` pointing to your local LAN IP. E.g.

```
10.0.0.211 teamraum gever
```


### LDAP Credentials

The default configuration uses the TeamraumDEV LDAP branch. You need to provide
the LDAP credentials using environment variables. The easiest way is to put
them into a `.env` file, which is automatically read by Docker Compose.

The credentials are needed by the Ianus backend and ogcore using different
environment variable names.

```
DJANGO_AUTH_LDAP_BIND_DN=<bind dn>
DJANGO_AUTH_LDAP_BIND_PASSWORD=<password>

PLONE_LDAP_BIND_UID=<bind dn>
PLONE_LDAP_BIND_PWD=<password>
```

Alternatively you can also start your own 389 ds instance but this will require
some additional setup. See 389 ds section for details.


## Startup

First pull all images to avoid building them locally.

You have to select the profile `all` as by default only a minimum set of services
is enabled.

```
docker-compose --profile all pull 
```

Then start all services with:

```
docker-compose --profile all up -d
```


## Setup

After the first startup you need to perform some initial setup.

### Add CAS service

```
docker-compose exec ianus-backend ./manage.py create_service all '.*' username
```

### Add admin user

```
docker-compose exec ianus-backend ./manage.py createsuperuser
```

### Create a policyless deployment

Open the URL http://localhost:8080/, go to the ZMI and click on "Install OneGov GEVER".
Select "Policyless Deployment" and "Policyless LDAP" and click ""Install OneGov GEVER".

### Import a bundle

You can either create your own bundle or use the provided example.

Got to http://localhost:8080/ogsite/@@import-bundle and provide the .json files
from your bundle. E.g. `configuration.json` and `workspaceroots.json` from
`example_bundles/teamraum.oggbundle`.

### Disable Secure Session Cookie

Currently we don't have an HTTPS setup yet. Thus Plone's session cookie secure
flag needs to be disabled. Got to the properties of the PAS session plugin
(acl_users/session) and uncheck the "Only Send Cookie Over HTTPS" setting.

You should now be able to access the application using the hostnames you
defined at port 8088 (e.g. http://teamraum:8088 or http://gever:8088).

## Building the Docker images

Before building the images, you need the source checkouts that are currently
managed with buildout (mr.developer). Thus you first need to run buildout.

A Gitlab deploy token needs to be provided in the environment variable
`GITLAB_DEPLOY_TOKEN` to be able to download private Python packages from
git.4teamwork.ch.

```
export GITLAB_DEPLOY_TOKEN=<gldt-xxx>
```

To build all images simply run:

```
docker-compose --profile all build
```

There are three images that are built from this repo:

- oghttpd 
- ogcore
- ogsolr

### oghttpd

An Apache httpd image serving as reverse proxy with the needed rewrite rules.
The Apache config is genereated on startup with settings from environment variables.
The various settings are documented in its own README (see httpd directory).

### ogcore

This image contains the opengever.core Zope instance based on the 4teamwork/plone
image.

The Python packages are installed using pip. The dependencies are declared in
the requirements files `requirements-core.txt` and `requirements-deployment.txt`.
Those files are managed manually and need to be updated if new requirements are
introduced or versions change.

### ogsolr

A Solr image containing our Solr configuration.


## 389ds

If you want to run your own 389 DS instance either create a `docker-compose.override.yml`
file and add the content from `docker-compose.389ds.yml` or include the
`docker-compose.389ds.yml` file using the `-f` option of Docker Compose.

Before you can use your 389 DS instance, you need to setup a database and a suffix.
Then you need to create an initial LDAP structure containing groups and users. 

### Create Database and Suffix

```
docker-compose exec 389ds dsconf localhost backend create --suffix="dc=example,dc=com" --be-name="example"
```

### Load initial LDAP structure

```
docker-compose exec 389ds /bin/sh
ldapadd -D "cn=Directory Manager" -H ldap://localhost:3389 -x -W
```

```
version: 1

dn: dc=example,dc=com
objectClass: domain
objectClass: top
dc: example

dn: ou=Users,dc=example,dc=com
objectClass: organizationalUnit
objectClass: top
ou: Users

dn: cn=donald.duck@entenhausen.net,ou=Users,dc=example,dc=com
objectClass: inetOrgPerson
objectClass: inetUser
objectClass: organizationalPerson
objectClass: person
objectClass: top
cn: donald.duck@entenhausen.net
sn: Duck
givenName: Donald
mail: donald.duck@entenhausen.net
uid: donald.duck@entenhausen.net
userPassword:: e1BCS0RGMl9TSEEyNTZ9QUFBSUFCS2MxcDlTZjJZQUxEUGphTGNxTFdYdThwW
 WpNanRvMlg4SUpIWnhIWk1vcGNuTzRLYXlqemxZQzJ4T2toZzM2ckE4L2dNcitQaGNqeVlSUHpo
 RFhyL2p4VWFXdE5ZbDR4cGMyVExlb3ZwN0liSXhGTy9aVmxWMmFkMkF3b3dPbDRBSDRCRUZMSVU
 5U2JMTDVzSXRKWWhOVzg5Ym1zTkFYOEhUbkNkNFgvZFdSNFEzbmlQNE1zcEo4VnNIS3NvdjhLb2
 UrYmZOWXdVSFVhaVFRUWExWGFRNG5vc2tESWo3K3MxckRYYzlBbDZuSkZ2NEhpZnp0MnkyZGhEM
 Fh5WTk1YTIzU0NtRTVtMlRKT3p4TUsyUFN0c3hCYkpiUThOVDhnN3R2TmJWK044cE9PNVZ1YjY0
 WUFSN0tBdjFxWWUwaG56SFdEeUZhTFd1M201RTRZcE10VnJUWlUrQ25xbFJxQkJycmhzWUxNMTJ
 NS0tOckgwL1ZxcG5EaGZBcUIxUk5pMS9oZ3g5RFBxNEdPbHFNSTZUaFUyS0lsQysrNzRsNE9RQV
 hjeFRpZHB1

dn: ou=Groups,dc=example,dc=com
objectClass: organizationalUnit
objectClass: top
ou: Groups

dn: cn=tr_administrators,ou=Groups,dc=example,dc=com
objectClass: groupOfUniqueNames
objectClass: top
cn: tr_administrators

dn: cn=tr_users,ou=Groups,dc=example,dc=com
objectClass: groupOfUniqueNames
objectClass: top
cn: tr_users
uniqueMember: cn=donald.duck@entenhausen.net,ou=Users,dc=example,dc=com

dn: cn=tr_creators,ou=Groups,dc=example,dc=com
objectClass: groupOfUniqueNames
objectClass: top
cn: tr_creators
uniqueMember: cn=donald.duck@entenhausen.net,ou=Users,dc=example,dc=com
```


## Issues

Solr config is not updated if changed in the image. The config is copied to
the core directory only once when the core is created inititally.
