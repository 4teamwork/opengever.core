from ftw.upgrade import UpgradeStep
from opengever.mail.behaviors import IMailInAddressMarker
from zope.interface import noLongerProvides


MAIL_BEHAVIOR = 'opengever.mail.behaviors.IMailInAddress'


class RemoveMailInBehavior(UpgradeStep):

    def __call__(self):
        # Remove IMailInAddress behavior from all FTIs
        portal_types = self.portal.portal_types
        ftis = portal_types.values()
        for fti in ftis:
            if hasattr(fti, 'behaviors') and MAIL_BEHAVIOR in fti.behaviors:
                self.remove_behavior(fti, MAIL_BEHAVIOR)

        # Remove IMailInAddressMarker from all objects
        catalog = self.getToolByName('portal_catalog')
        query = {'object_provides': IMailInAddressMarker.__identifier__}
        msg = 'Remove IMailInAddressMarker from objects providing it'

        for obj in self.objects(query, msg):
            noLongerProvides(obj, IMailInAddressMarker)
            catalog.reindexObject(obj, idxs=['object_provides'])

    def remove_behavior(self, fti, behavior):
        """Remove a behavior from an FTI without changing the order of the
        any other behaviors.
        """
        new_behaviors = [b for b in fti.behaviors if not b == behavior]
        fti.behaviors = tuple(new_behaviors)
