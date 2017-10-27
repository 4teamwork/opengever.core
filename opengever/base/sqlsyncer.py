from Acquisition import aq_base
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
import logging


logger = logging.getLogger('opengever.sqlsyncer')


class SqlSyncer(object):
    """Base class to sync plone objects to an sql index."""

    def __init__(self, obj, event):
        self.obj = obj
        self.event = event

        if not self.is_uninstalling_plone():
            self.obj_id = self.get_object_id()

    def is_uninstalling_plone(self):
        return IObjectRemovedEvent.providedBy(self.event) \
            and IPloneSiteRoot.providedBy(self.event.object)

    def get_object_id(self):
        intids = getUtility(IIntIds)
        try:
            return intids.getId(self.obj)
        except KeyError:
            try:
                # In some case (remote task updating etc)
                # only the base_object provides an intid.
                int_id = intids.getId(aq_base(self.obj))
                logger.info('Used aq_base(obj) fallback to get intid.')
                return int_id
            except KeyError:
                # The intid event handler didn't create an intid for this
                # object yet. The event will be fired again after creating the
                # id.
                return None

    def sync(self):
        if self.is_uninstalling_plone():
            logger.warn(
                'Synchronisation of object {!r} skipped, '
                'plone site is being uninstalled.'.format(self.obj))
            return

        if self.obj_id is None:
            logger.warn('Synchronisation of object {!r} skipped, '
                        'no intid exists for this object.'.format(self.obj))
            return

        return self.sync_with_sql()

    def sync_with_sql(self):
        raise NotImplementedError()
