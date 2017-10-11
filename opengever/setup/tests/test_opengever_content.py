from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import applyProfile


class TestDocumentTemplates(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentTemplates, self).setUp()
        self.grant('Manager')
        applyProfile(self.portal, 'opengever.setup.tests:templates')

    def test_template_documents_are_loaded(self):
        template = self.portal['vorlagen']['template-1']
        rt = api.portal.get_tool('portal_repository')
        self.assertIsNotNone(template.file)

    def test_sablon_templates_are_loaded(self):
        template = self.portal['vorlagen']['sablon-template-1']
        rt = api.portal.get_tool('portal_repository')

        self.assertIsNotNone(template.file)

    def test_commitee_models_are_created(self):
        committee = self.portal['kommitees']['committee-1']
        committee_model = committee.load_model()

        self.assertIsNotNone(committee_model)
        self.assertEqual(u'Testkommission', committee_model.title)
