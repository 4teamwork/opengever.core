#!/usr/bin/python

import sys
import urllib.request
import urllib.parse
import os


def post_message(url, recipient, message_txt):
    """Post an email message to the given url
    """

    if not url:
        print("Invalid url.")
        print("usage: mta2plone.py url <recipient>")
        sys.exit(64)

    data = {'mail': message_txt}
    if recipient and len(recipient) > 0:
        data['recipient'] = recipient

    try:
        data = urllib.parse.urlencode(data)
        data = data.encode('ascii')
        result = urllib.request.urlopen(url, data).read()
    except (IOError, EOFError) as e:
        print("ftw.mail error: could not connect to server", e)
        sys.exit(73)

    try:
        exitcode, errormsg = result.split(b':')
        if exitcode != b'0':
            print('Error %s: %s' % (exitcode.decode('utf8'), errormsg.decode('utf8')))
            sys.exit(int(exitcode))
    except ValueError:
        print('Unknown error.')
        sys.exit(69)

    sys.exit(0)


if __name__ == '__main__':
    # This gets called by the MTA when a new message arrives.
    # The mail message file gets passed in on the stdin

    # Get the raw mail
    message_txt = sys.stdin.read()

    url = ''
    if len(sys.argv) > 1:
        url = sys.argv[1]

    recipient = ''
    # If mta2plone is executed as external command by the MTA, the
    # environment variable ORIGINAL_RECIPIENT contains the entire
    # recipient address, before any address rewriting or aliasing
    recipient = os.environ.get('ORIGINAL_RECIPIENT')

    if len(sys.argv) > 2:
        recipient = sys.argv[2]

    post_message(url, recipient, message_txt)
