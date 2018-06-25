from ftw.upgrade import UpgradeStep
from Products.CMFPlone.utils import base_hasattr


class RemoveAdHocTemplateFieldFromCommitteeContainer(UpgradeStep):
    """Remove ad-hoc template field from committee container.
    """

    def __call__(self):
        self.delete_ad_hoc_template_field()

    def delete_ad_hoc_template_field(self):
        for container in self.objects(
                {'portal_type': 'opengever.meeting.committeecontainer'},
                'Delete ad-hoc templates'):

            if base_hasattr(container, 'ad_hoc_template'):
                delattr(container, 'ad_hoc_template')
