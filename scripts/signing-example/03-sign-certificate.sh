#!/bin/sh
/System/Library/OpenSSL/misc/CA.pl -sign

# Enter pass phrase for ./demoCA/private/cakey.pem: [Password for CA private key (helloca)]

# Sign the certificate? [y/n]:y
# 1 out of 1 certificate requests certified, commit? [y/n]y

echo "Signed certificate is in ./newcert.pem"
