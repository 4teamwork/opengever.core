from ftw.upgrade import UpgradeStep
from opengever.contact.contactfolder import ContactFolder
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class ChangeContactFolderClass(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.contact.upgrades:4501')
        self.migrate_contactfolder_class()

    def migrate_contactfolder_class(self):
        query = {'portal_type': 'opengever.contact.contactfolder'}
        msg = 'Migrate repositoryroot class'
        for repositoryroot in self.objects(query, msg, savepoints=500):
            self.migrate_object(repositoryroot)

    def migrate_object(self, obj):
        self.migrate_class(obj, ContactFolder)
        notify(ObjectModifiedEvent(obj))
