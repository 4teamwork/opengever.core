#!/bin/sh

openssl rsa -in newkey.pem -out key.key
# Enter pass phrase for newkey.pem: [Private key passphrase (hellokey)]

echo "Private key without passphrase is in ./key.key"

mv newcert.pem cert.pem
echo "Signed certificate is in ./cert.pem"
