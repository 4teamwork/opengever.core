#! /bin/sh

/usr/local/bin/configure-postfix.py

postmap lmdb:/etc/postfix/virtual
postalias /etc/aliases
postmap -F lmdb:/etc/postfix/sni

exec postfix start-fg
