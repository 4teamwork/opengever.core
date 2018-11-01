from opengever.testing import IntegrationTestCase


class TestTaskPrincipals(IntegrationTestCase):

    def test_return_a_list_of_all_users_and_groups_which_are_able_to_see_the_task(self):
        self.login(self.regular_user)

        self.assertEqual(
            [u'kathi.barfuss', u'fa_users'], self.task.get_principals())

    def test_does_respect_blocked_role_inheritance(self):
        self.login(self.regular_user)

        self.assertEqual(
            [u'kathi.barfuss'], self.task_in_protected_dossier.get_principals())
