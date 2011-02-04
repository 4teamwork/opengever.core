from DateTime import DateTime
from five import grok
from ftw.mail import utils
from ftw.mail.mail import IMail
from plone.indexer import indexer
from opengever.tabbedview.helper import readable_ogds_author

#indexes
@indexer(IMail)
def document_author(obj):
    """ doucment_author indexer, return the Sender Adress """
    document_author = utils.get_header(obj.msg, 'From')
    document_author = document_author.replace('<', '&lt;')
    document_author = document_author.replace('>', '&gt;')
    return document_author
grok.global_adapter(document_author, name='document_author')


@indexer(IMail)
def document_date(obj):
    """ document_date indexer, return the from date of the mail """
    document_date = utils.get_date_header(obj.msg, 'Date')
    return DateTime(document_date)
grok.global_adapter(document_date, name="document_date")


@indexer(IMail)
def receipt_date(obj):
    """Returns the receipt date of the mail.
       We currently approximate this date by using the
       document date"""
    # TODO: Parse Received-values of header mail
    document_date = utils.get_date_header(obj.msg, 'Date')
    return DateTime(document_date)
grok.global_adapter(receipt_date, name='receipt_date')

@indexer(IMail)
def sortable_author(obj):
    """Index to allow users to sort on document_author."""
    author = document_author(obj)
    readable_author = readable_ogds_author(obj, author())
    return readable_author
grok.global_adapter(sortable_author, name='sortable_author')