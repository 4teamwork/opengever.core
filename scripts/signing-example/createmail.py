#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to create a sample signed mail.

Requires M2Crypto which is not available by default. Best create a virtualenv
and install it there, then run this script from within that virtualenv.
"""
from M2Crypto import BIO
from M2Crypto import SMIME
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import formatdate


SSL_KEY_FILE = 'key.key'
SSL_CERT_FILE = 'cert.pem'


def create_signed_sample_mail():
    multipart = MIMEMultipart()
    multipart.attach(MIMEText('Hello, i\'m a signed mail.'))

    smime = SMIME.SMIME()
    smime.load_key(SSL_KEY_FILE, SSL_CERT_FILE)
    p7 = smime.sign(BIO.MemoryBuffer(multipart.as_string()), SMIME.PKCS7_DETACHED)

    out_bio = BIO.MemoryBuffer()
    out_bio.write('From: from@example.com\n')
    out_bio.write('To: to@example.com\n')
    out_bio.write('Date: {}\n'.format(formatdate(localtime=True)))
    out_bio.write('Subject: Hello\n')

    data_bio = BIO.MemoryBuffer(multipart.as_string())
    smime.write(out_bio, p7, data_bio)

    with open('signed.p7m', 'w') as signed:
        signed.write(out_bio.read())


if __name__ == '__main__':
    create_signed_sample_mail()
