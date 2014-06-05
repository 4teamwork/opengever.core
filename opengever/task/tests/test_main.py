from ftw.builder import Builder
from ftw.builder import create
from opengever.task.browser.accept.main import IChooseMethodSchema
from opengever.task.browser.accept.main import MethodValidator
from opengever.testing import FunctionalTestCase
from zope.interface import Invalid


class TestMethodValidator(FunctionalTestCase):

    def setUp(self):
        super(TestMethodValidator, self).setUp()

        self.user, self.org_unit, self.admin_unit, self.hugo = create(
            Builder('fixture').with_all_unit_setup().with_hugo_boss())

    def test_pass_if_value_is_participate(self):
        task = create(Builder('task')
                      .having(responsible_client='client1'))

        validator = MethodValidator(task, self.portal.REQUEST, None,
                                    IChooseMethodSchema['method'], None)

        validator.validate('participate')

    def test_pass_if_current_user_is_assigned_to_responsible_client(self):
        task = create(Builder('task')
                      .having(responsible_client='client1'))

        validator = MethodValidator(task, self.portal.REQUEST, None,
                                    IChooseMethodSchema['method'], None)

        validator.validate('existing_dossier')

    def test_raise_invalid_if_current_user_is_not_assigned_to_responsible_client(self):
        create(Builder('org_unit').id('client2'))
        task = create(Builder('task')
                      .having(responsible_client='client2'))

        validator = MethodValidator(task, self.portal.REQUEST, None,
                                    IChooseMethodSchema['method'], None)

        with self.assertRaises(Invalid):
            validator.validate('existing_dossier')
