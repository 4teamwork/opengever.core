# Running opengever.core with Docker

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

Before you can try out the application you need to perform some initial setup.

## 389ds

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

## Ianus

### Add service

```
docker-compose exec ianus-backend ./manage.py create_service teamraum '^http://teamraum.*' username
```

### Add admin user

```
docker-compose exec ianus-backend ./manage.py createsuperuser
```

## OG Core

### Create policyless deployment

Open the URL http://localhost:8080/, go to the ZMI and click on "Install OneGov GEVER".
Select "Policyless Deployment" and "Policyless LDAP" and click ""Install OneGov GEVER".

### Import teamraum bundle

Got to http://localhost:8080/ogsite/@@import-bundle and provide `configuration.json`
and `workspaceroots.json` from `example_bundles/teamraum.oggbundle`.


## Using the application

Currently the application only works when using an address that's accessible
from inside Docker. Thus localhost or 127.0.0.1 does not work.
Use your LAN IP or create an entry in your `/etc/hosts` file that points to your
LAN IP.

Now you can open the application in your browser on port 8081, e.g. http://teamraum:8081
