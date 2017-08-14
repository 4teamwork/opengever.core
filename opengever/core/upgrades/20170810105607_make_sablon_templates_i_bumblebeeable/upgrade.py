from ftw.bumblebee import get_service_v3
from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.upgrade import UpgradeStep
from opengever.bumblebee import is_bumblebee_feature_enabled
from plone import api


class MakeSablonTemplatesIBumblebeeable(UpgradeStep):
    """Make sablon templates i bumblebeeable.
    """

    def __call__(self):
        self.install_upgrade_profile()
        catalog = api.portal.get_tool('portal_catalog')
        query = {'portal_type': 'opengever.meeting.sablontemplate'}
        msg = 'Add bumblebee-previews for sablontemplates.'

        for obj in self.objects(query, msg):
            IBumblebeeDocument(obj).update_checksum()
            catalog.reindexObject(obj, idxs=['object_provides'],
                                  update_metadata=False)

            if is_bumblebee_feature_enabled():
                get_service_v3().trigger_storing(obj, deferred=True)
