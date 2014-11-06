from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import applyProfile


class TestDocumentTemplates(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentTemplates, self).setUp()
        self.grant('Manager')
        self.dossier = create(Builder('templatedossier').titled(u'Vorlagen'))
        applyProfile(self.portal, 'opengever.setup.tests:templates')

    def test_templates_are_loaded_with_working_initial_version(self):
        template = self.portal['vorlagen']['template-1']
        rt = api.portal.get_tool('portal_repository')

        self.assertIsNotNone(template.file)
        version_0_template = rt.retrieve(template, 0).object
        self.assertIsNotNone(version_0_template.file)
