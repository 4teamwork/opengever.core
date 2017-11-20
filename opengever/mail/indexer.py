from ftw.mail.mail import IMail
from plone.indexer import indexer


@indexer(IMail)
def checked_out(obj):
    """Empty string checked out indexer, because we need an index value
    for sorted listings, but a mail can't be checked out so we return a
    empty string."""

    return ''
