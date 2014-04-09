from ftw.builder import Builder
from ftw.builder import create
from opengever.task.browser.accept.main import IChooseMethodSchema
from opengever.task.browser.accept.main import MethodValidator
from opengever.testing import FunctionalTestCase
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from plone.app.testing import TEST_USER_ID
from zope.interface import Invalid


class TestMethodValidator(FunctionalTestCase):

    def test_pass_if_value_is_participate(self):
        create_client(clientid='client1', title="Client 1" )
        task = create(Builder('task')
                      .having(responsible_client='client1'))

        validator = MethodValidator(task, self.portal.REQUEST, None,
                                    IChooseMethodSchema['method'], None)

        validator.validate('participate')

    def test_pass_if_current_user_is_assigned_to_responsible_client(self):
        client1 = create_client(clientid='client1', title="Client 1" )
        create_ogds_user(TEST_USER_ID, assigned_client=[client1, ])

        task = create(Builder('task')
                      .having(responsible_client='client1'))

        validator = MethodValidator(task, self.portal.REQUEST, None,
                                    IChooseMethodSchema['method'], None)

        validator.validate('existing_dossier')

    def test_raise_invalid_if_current_user_is_not_assigned_to_responsible_client(self):
        create_client(clientid='client1', title="Client 1" )
        create_ogds_user(TEST_USER_ID, assigned_client=[])

        task = create(Builder('task')
                      .having(responsible_client='client1'))

        validator = MethodValidator(task, self.portal.REQUEST, None,
                                    IChooseMethodSchema['method'], None)

        with self.assertRaises(Invalid):
            validator.validate('existing_dossier')
