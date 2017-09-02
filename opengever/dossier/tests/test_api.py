from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.interfaces import IEmailAddress
from opengever.api.testing import RelativeSession
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ZSERVER_TESTING
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD


class TestDossierApi(FunctionalTestCase):
    """Test plone.rest endpoints on dossiers."""

    layer = OPENGEVER_FUNCTIONAL_ZSERVER_TESTING

    def setUp(self):
        super(TestDossierApi, self).setUp()

        # Set up the requests wrapper
        self.portal = self.layer['portal']
        self.api = RelativeSession(self.portal.absolute_url())
        self.api.headers.update({'Accept': 'application/json'})
        self.api.auth = (TEST_USER_NAME, TEST_USER_PASSWORD)

        # Set up a minimal GEVER site
        self.repo = create(Builder('repository_root'))
        self.repofolder = create(Builder('repository').within(self.repo))
        self.dossier = create(Builder('dossier').within(self.repofolder))

    def test_dossier_attributes(self):
        site_id = api.portal.get().id
        path_segments = [s for s in self.dossier.getPhysicalPath()
                         if s != site_id]
        path_segments.append('attributes')
        dossier_attributes_path = '/'.join(path_segments)
        attributes = self.api.get(dossier_attributes_path).json()

        # Catch future changes to the API
        self.assertEqual(1, len(attributes.keys()))

        self.assertIn('email', attributes)

        dossier_email = IEmailAddress(
            self.request).get_email_for_object(self.dossier)
        self.assertEqual(dossier_email, attributes['email'])
