from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.document.behaviors import IBaseDocument
from opengever.inbox.inbox import IInbox
from opengever.inbox.yearfolder import IYearFolder
from opengever.ogds.base.utils import get_current_org_unit
from plone.indexer import indexer


@indexer(IBaseDocument)
def client_id_for_inbox_documents(obj):
    """Indexer which indexs the current_org_unit for
    documents which are inside an inbox or a yearfolder."""

    parent = aq_parent(aq_inner(obj))

    if IInbox.providedBy(parent) or IYearFolder.providedBy(parent):
        return get_current_org_unit().id()
    return None

grok.global_adapter(client_id_for_inbox_documents, name='client_id')
