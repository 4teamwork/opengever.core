from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import applyProfile


class TestSetupDefaultContentProfile(FunctionalTestCase):

    def setUp(self):
        super(TestSetupDefaultContentProfile, self).setUp()
        self.grant('Manager')
        applyProfile(self.portal, 'opengever.setup:default_content')

    def test_default_content_workspace_root_placeful_workflow(self):
        workspace_root = self.portal['workspaces']

        placeful_workflow = api.portal.get_tool('portal_placeful_workflow')
        config = placeful_workflow.getWorkflowPolicyConfig(workspace_root)
        self.assertEqual(
            "opengever_workspace_policy", config.getPolicyInId())
        self.assertEqual(
            "opengever_workspace_policy", config.getPolicyBelowId())

    def test_default_content_inbox_placeful_workflow(self):
        inbox = self.portal['eingangskorb']

        placeful_workflow = api.portal.get_tool('portal_placeful_workflow')
        config = placeful_workflow.getWorkflowPolicyConfig(inbox)
        self.assertEqual(
            "opengever_inbox_policy", config.getPolicyInId())
        self.assertEqual(
            "opengever_inbox_policy", config.getPolicyBelowId())


class TestExampleContentDefaultContentProfile(FunctionalTestCase):

    def setUp(self):
        super(TestExampleContentDefaultContentProfile, self).setUp()
        self.grant('Manager')
        applyProfile(self.portal, 'opengever.examplecontent:default_content')

    def test_default_content_workspace_root_placeful_workflow(self):
        workspace_root = self.portal['workspaces']

        placeful_workflow = api.portal.get_tool('portal_placeful_workflow')
        config = placeful_workflow.getWorkflowPolicyConfig(workspace_root)
        self.assertEqual(
            "opengever_workspace_policy", config.getPolicyInId())
        self.assertEqual(
            "opengever_workspace_policy", config.getPolicyBelowId())

    def test_default_content_inbox_placeful_workflow(self):
        inbox_afi = self.portal['eingangskorb']['eingangskorb_afi']

        placeful_workflow = api.portal.get_tool('portal_placeful_workflow')
        config = placeful_workflow.getWorkflowPolicyConfig(inbox_afi)
        self.assertEqual(
            "opengever_inbox_policy", config.getPolicyInId())
        self.assertEqual(
            "opengever_inbox_policy", config.getPolicyBelowId())

        inbox_stv = self.portal['eingangskorb']['eingangskorb_stv']

        placeful_workflow = api.portal.get_tool('portal_placeful_workflow')
        config = placeful_workflow.getWorkflowPolicyConfig(inbox_stv)
        self.assertEqual(
            "opengever_inbox_policy", config.getPolicyInId())
        self.assertEqual(
            "opengever_inbox_policy", config.getPolicyBelowId())
