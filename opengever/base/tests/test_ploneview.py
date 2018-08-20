from opengever.testing import IntegrationTestCase


class TestGeverPloneView(IntegrationTestCase):

    def test_show_editableborder_is_true_when_only_workflow_transitions_are_visible(self):
        self.login(self.administrator)

        self.set_workflow_state('dossier-state-inactive', self.empty_dossier)
        self.empty_dossier.__ac_local_roles_block__ = True
        self.empty_dossier.reindexObjectSecurity()

        self.assertTrue(
            self.empty_dossier.unrestrictedTraverse('plone').showEditableBorder())
