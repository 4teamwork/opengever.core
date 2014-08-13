from ftw.upgrade import UpgradeStep
from opengever.mail.behaviors import IMailInAddressMarker
from zope.interface import noLongerProvides


class RemoveMailInBehavior(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.inbox.upgrades:2603')

        catalog = self.getToolByName('portal_catalog')

        query = {'object_provides': IMailInAddressMarker.__identifier__}
        msg = 'Remove IMailInAddressMarker from objects providing it'

        for obj in self.objects(query, msg):
            noLongerProvides(obj, IMailInAddressMarker)
            catalog.reindexObject(obj, idxs=['object_provides'])
