from five import grok
from ftw.mail.mail import IMail
from plone.indexer import indexer


@indexer(IMail)
def checked_out( obj ):
    return ''
grok.global_adapter( checked_out, name='checked_out' )
