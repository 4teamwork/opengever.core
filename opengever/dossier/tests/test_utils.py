from opengever.dossier.utils import is_dossierish_portal_type
from opengever.testing import IntegrationTestCase
from plone import api


class TestDossierUtils(IntegrationTestCase):

    def test_is_dossierish_portal_type(self):
        self.login(self.regular_user)
        portal_types = api.portal.get_tool('portal_types')
        self.assertItemsEqual(
            [
                'opengever.dossier.businesscasedossier',
                'opengever.dossier.dossiertemplate',
                'opengever.meeting.meetingdossier',
                'opengever.private.dossier',
            ],
            [
                portal_type_name for portal_type_name
                in portal_types.listContentTypes()
                if is_dossierish_portal_type(portal_type_name)
            ]
        )
