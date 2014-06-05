from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from opengever.task.task import ITask
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestAutoCompleteWidget(FunctionalTestCase):

    def setUp(self):
        super(TestAutoCompleteWidget, self).setUp()
        self.grant('Member', 'Manager')
        self.widget = AutocompleteFieldWidget(
            ITask['issuer'], self.portal.REQUEST)

        self.user, self.org_unit, self.admin_unit, self.hugo = create(
            Builder('fixture').with_all_unit_setup().with_hugo_boss())
        create(Builder('ogds_user')
               .in_group(self.org_unit.users_group())
               .having(userid='franz.michel'))

    def test_initally_no_hidden_terms_are_set(self):
        task = create(Builder('task'))

        self.widget.context = task
        source = self.widget.bound_source

        self.assertItemsEqual(
            [u'hugo.boss', u'franz.michel', TEST_USER_ID, u'inbox:client1'],
            [i.value for i in source])

        self.assertEquals([], source.hidden_terms)

    def test_not_existing_term_in_vocabulary_is_not_shown_in_listing(self):
        task = create(Builder('task').having(issuer='not.existing'))

        self.widget.context = task

        self.assertItemsEqual(
            [u'hugo.boss', u'franz.michel', TEST_USER_ID, u'inbox:client1'],
            [i.value for i in self.widget.bound_source])

    def test_not_existing_term_in_vocabulary_is_included_in_hidden_terms(self):
        task = create(Builder('task').having(issuer='not.existing'))

        self.widget.context = task
        self.assertEquals([u'not.existing'],
                          self.widget.bound_source.hidden_terms)
