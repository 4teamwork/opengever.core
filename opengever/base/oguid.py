from five import grok
from opengever.globalsolr.interfaces import ISearch
from opengever.base.interfaces import IOGUid
from opengever.ogds.base.utils import get_client_id
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class OGUidProvider(grok.GlobalUtility):
    """Interface for the OGUid utility which generates client comprehensive
    unique ids based on the client ID and the zope.intid.
    """

    grok.provides(IOGUid)

    def get_id(self, context):
        """Returns the oguid of `context`.
        """
        client_id = get_client_id()
        intids = getUtility(IIntIds)
        return '%s:%i' % (client_id, intids.getId(context))

    def is_on_current_client(self, oguid):
        """Returns `True` if the object with this `oguid` is stored on the
        current client, otherwise `False`.
        """
        client_id = get_client_id()
        cid, iid = oguid.split(':', 1)
        return cid == client_id

    def get_object(self, oguid):
        """Returns the object with the `oguid`, if it exists on the current
        client. Otherwise it returns `None`.
        """
        client_id = get_client_id()
        intids = getUtility(IIntIds)
        cid, iid = oguid.split(':', 1)
        if cid != client_id:
            return None
        else:
            return intids.getObject(int(iid))

    def get_flair(self, oguid):
        """Returns the flair of this ``oguid``.
        """
        solr_util = getUtility(ISearch)
        cid, iid = oguid.split(':', 1)
        solr_response = solr_util({'client_id': cid, 'intid': iid})
        if len(solr_response) > 0:
            return solr_response[0]
        else:
            return None
