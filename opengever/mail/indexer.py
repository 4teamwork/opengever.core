from collective import dexteritytextindexer
from five import grok
from ftw.mail.mail import IMail
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from plone.indexer import indexer
from zope.component import getAdapter, getUtility


@indexer(IMail)
def checked_out(obj):
    """Empty string checked out indexer, because we need an index value
    for sorted listings, but a mail can't be checked out so we return a
    empty string."""

    return ''
grok.global_adapter(checked_out, name='checked_out')


class SearchableTextExtender(grok.Adapter):
    """Specifix SearchableText Extender for the mail"""

    grok.context(IMail)
    grok.name('IOGMail')
    grok.implements(dexteritytextindexer.IDynamicTextIndexExtender)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        searchable = []
        # append some other attributes to the searchableText index
        # reference_number
        refNumb = getAdapter(self.context, IReferenceNumber)
        searchable.append(refNumb.get_number())

        # sequence_number
        seqNumb = getUtility(ISequenceNumber)
        searchable.append(str(seqNumb.get_number(self.context)))

        return ' '.join(searchable)
