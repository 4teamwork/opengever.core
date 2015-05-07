from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from opengever.dossier.templatedossier import TemplateDossier
from plone import api
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class MigrateTemplateDossierClass(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-opengever.dossier.upgrades:4303')
        self.migrate_template_dossiers()

    def migrate_template_dossiers(self):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            portal_type='opengever.dossier.templatedossier')

        with ProgressLogger('Migrating templatedossier class', brains) as step:
            for brain in brains:
                self.migrate_object(brain.getObject())
                step()

    def migrate_object(self, obj):
        self.migrate_class(obj, TemplateDossier)
        notify(ObjectModifiedEvent(obj))
