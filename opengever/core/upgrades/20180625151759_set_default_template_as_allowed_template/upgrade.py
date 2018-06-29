from ftw.upgrade import UpgradeStep
from opengever.meeting.committee import ICommittee
from plone.uuid.interfaces import IUUID


class SetDefaultTemplateAsAllowedTemplate(UpgradeStep):
    """Set default template as allowed template.
    """

    def __call__(self):
        self.install_upgrade_profile()

        query = {'object_provides': [ICommittee.__identifier__]}
        for obj in self.objects(
                query, 'Set default template as allowed template in committees'):
            container_ad_hoc_template = obj.get_ad_hoc_template()
            if container_ad_hoc_template is not None:
                obj.allowed_ad_hoc_agenda_item_templates = [IUUID(container_ad_hoc_template)]
