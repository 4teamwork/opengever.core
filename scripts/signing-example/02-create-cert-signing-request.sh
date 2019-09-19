#!/bin/sh
/System/Library/OpenSSL/misc/CA.pl -newreq

# Enter PEM pass phrase:                        hellokey

# Country Name (2 letter code):                 CH
# State or Province Name (full name):           Bern
# Locality Name (eg, city):                     Bern
# Organization Name (eg, company):              Mailer
# Organizational Unit Name (eg, section):
# Common Name (e.g. server FQDN or YOUR name):  mailer.example.org
# Email Address:                                mailer@mailer.example.org

# A challenge password:                         hellochallenge

echo "Certificate Signing Request is in ./newreq.pem"
echo "Private key is in ./newkey.pem"
