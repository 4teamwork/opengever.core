from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from opengever.task.task import ITask
from opengever.testing import Builder
from opengever.testing import create
from opengever.testing import FunctionalTestCase
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from opengever.testing import set_current_client_id


class TestAutoCompleteWidget(FunctionalTestCase):

    def setUp(self):
        super(TestAutoCompleteWidget, self).setUp()
        self.grant('Member', 'Manager')
        self.widget = AutocompleteFieldWidget(
            ITask['issuer'], self.portal.REQUEST)

    def test_initally_no_hidden_terms_are_set(self):
        create_client(clientid='client1')
        create_ogds_user('hugo.boss')
        create_ogds_user('franz.michel')
        set_current_client_id(self.portal)
        task = create(Builder('task'))

        self.widget.context = task
        source = self.widget.bound_source

        self.assertEquals(
            [u'hugo.boss', u'franz.michel', u'inbox:client1'],
            [i.value for i in source])

        self.assertEquals([], source.hidden_terms)

    def test_not_existing_term_in_vocabulary_is_not_shown_in_listing(self):
        create_client(clientid='client1')
        create_ogds_user('hugo.boss')
        create_ogds_user('franz.michel')
        set_current_client_id(self.portal)
        task = create(Builder('task').having(issuer='not.existing'))

        self.widget.context = task

        self.assertNotIn(
            'not.existing', [i.value for i in self.widget.bound_source])

    def test_not_existing_term_in_vocabulary_is_included_in_hidden_terms(self):
        create_client(clientid='client1')
        create_ogds_user('hugo.boss')
        create_ogds_user('franz.michel')
        set_current_client_id(self.portal)
        task = create(Builder('task').having(issuer='not.existing'))

        self.widget.context = task
        self.assertEquals([u'not.existing'], self.widget.bound_source.hidden_terms)
