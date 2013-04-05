from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from opengever.mail.interfaces import ISendDocumentConf
from opengever.mail.mail import OGMail
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class AddRegistryEntries(UpgradeStep):

    def __call__(self):
        self.update_registry_entries([ISendDocumentConf, ])

    # TODO: could maybe moved to ftw.upgrade
    # as an default upgradestep helper method
    def update_registry_entries(self, interfaces):
        registry = getUtility(IRegistry)
        # update the registry entries
        for interface in interfaces:
            registry.registerInterface(interface)

class MigrateMailClass(UpgradeStep):

    def __call__(self):
        catalog = self.getToolByName('portal_catalog')
        brains = catalog(portal_type='ftw.mail.mail')

        with ProgressLogger('Migrating ftw.mail.mail class', brains) as step:
            for brain in brains:
                self.migrate_obj(brain.getObject())
                step()

    def migrate_obj(self, obj):
        self.migrate_class(obj, OGMail)
        notify(ObjectModifiedEvent(obj))

