from opengever.base.interfaces import IContextActions
from opengever.testing import IntegrationTestCase
from zope.component import queryMultiAdapter


class TestPrivateDossierContextActions(IntegrationTestCase):

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_private_dossier_context_actions(self):
        self.login(self.regular_user)
        expected_actions = [u'delete', u'document_with_template', u'edit', u'zipexport']
        self.assertEqual(expected_actions, self.get_actions(self.private_dossier))

    def test_document_from_docugate_available_if_feature_enabled(self):
        self.login(self.regular_user)
        self.assertNotIn(u'document_from_docugate', self.get_actions(self.private_dossier))
        self.activate_feature('docugate')
        self.assertIn(u'document_from_docugate', self.get_actions(self.private_dossier))

    def test_document_with_oneoffixx_template_available_if_feature_enabled(self):
        self.login(self.regular_user)
        self.assertNotIn(u'document_with_oneoffixx_template',
                         self.get_actions(self.private_dossier))
        self.activate_feature('oneoffixx')
        self.assertIn(u'document_with_oneoffixx_template', self.get_actions(self.private_dossier))
