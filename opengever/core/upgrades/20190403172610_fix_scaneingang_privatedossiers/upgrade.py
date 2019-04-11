from ftw.upgrade import UpgradeStep
from plone import api
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent


class FixScaneingangPrivatedossiers(UpgradeStep):
    """Fix scaneingang privatedossiers.
    """

    def __call__(self):
        self.install_upgrade_profile()
        catalog = api.portal.get_tool('portal_catalog')

        dossiers = catalog(sortable_title='scaneingang',  # Exact match
                           portal_type='opengever.private.dossier')

        for brain in dossiers:
            if not brain.UID:
                dossier = brain.getObject()
                notify(ObjectCreatedEvent(dossier))
                dossier.reindexObject()
