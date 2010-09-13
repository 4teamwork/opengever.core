from five import grok
from opengever.base.interfaces import IOGUid
from opengever.octopus.tentacle.interfaces import ITentacleConfig
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
        config = getUtility(ITentacleConfig)
        intids = getUtility(IIntIds)
        return '%s:%i' % (config.cid, intids.getId(context))

    def is_on_current_client(self, oguid):
        """Returns `True` if the object with this `oguid` is stored on the
        current client, otherwise `False`.
        """
        config = getUtility(ITentacleConfig)
        cid, iid = oguid.split(':', 1)
        return cid == config.cid

    def get_object(self, oguid):
        """Returns the object with the `oguid`, if it exists on the current
        client. Otherwise it returns `None`.
        """
        config = getUtility(ITentacleConfig)
        intids = getUtility(IIntIds)
        cid, iid = oguid.split(':', 1)
        if cid != config.cid:
            return None
        else:
            return intids.getObject(int(iid))
