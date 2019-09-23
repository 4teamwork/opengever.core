#!/bin/sh
/System/Library/OpenSSL/misc/CA.pl -newca

# [ENTER] (create new)
# Enter PEM pass phrase:                             helloca

# Country Name (2 letter code):                      CH
# Locality Name (eg, city):                          Bern
# Organization Name (eg, company):                   CA Corp
# Organizational Unit Name (eg, section):
# Common Name (e.g. server FQDN or YOUR name):       cert.example.com
# Email Address:                                     cert@cert.example.com

# A challenge password:                              hellochallenge

# Enter pass phrase for ./demoCA/private/cakey.pem:  [PEM pass phrase from above (helloca)]

echo "Created CA in ./demoCa"
echo "CA's private key is in ./demoCA/private/cakey.pem"
echo "CA cert is in ./demoCA/cacert.pem"
