from email.header import make_header


def make_addr_header(fullname, address, charset='utf-8'):
    """Creates an RFC2047 compliant From: or To: header.

    (Makes sure encoded-words are only used for addr-name, but not for
    angle-addr or addr-spec. See http://tools.ietf.org/html/rfc2047#section-5)
    """

    if not isinstance(fullname, unicode):
        raise ValueError("Please pass unicode to make_addr_header()")

    # Implicitely decode as 'ascii' - this should never be an issue for
    address = unicode(address)

    header = make_header(
        [(fullname.encode(charset), charset),
         (u'<{}>'.format(address), None)])

    return header


def is_rfc822_ish_mimetype(mimetype):
    return mimetype in ('message/rfc822', 'application/pkcs7-mime')
