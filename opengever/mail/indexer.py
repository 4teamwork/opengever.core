from DateTime import DateTime
from five import grok
from plone.indexer import indexer
from ftw.mail.mail import IMail
from ftw.mail import utils


#indexes
@indexer(IMail)
def document_author(obj):
    """ doucment_author indexer, return the Sender Adress """
    return utils.get_header(obj.msg, 'From')
grok.global_adapter(document_author, name='document_author')


@indexer(IMail)
def document_date(obj):
        """ document_date indexer, return the from date of the mail """
        document_date = utils.get_date_header(obj.msg, 'Date')
        return DateTime(document_date)

grok.global_adapter(document_date, name="document_date")
