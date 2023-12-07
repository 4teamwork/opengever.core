from opengever.ogds.base.actor import INTERACTIVE_ACTOR_IDS
from opengever.ogds.base.tests import test_sources as base
from opengever.tasktemplates.sources import TaskResponsibleSource
from opengever.tasktemplates.sources import TaskTemplateIssuerSource


class TestTaskTemplateIssuerSource(base.TestUsersContactsInboxesSource):

    def setUp(self):
        super(TestTaskTemplateIssuerSource, self).setUp()
        self.source = TaskTemplateIssuerSource(self.portal)

    def test_interactive_users_are_valid(self):
        for actor_id in INTERACTIVE_ACTOR_IDS:
            self.assertIn(actor_id, self.source)

    def test_search_interactive_users(self):
        result = self.source.search('Resp')

        # Filter out user IDs that match but we're not interested in
        result = [r for r in result if r.value != 'committee_responsible']

        self.assertEquals(1, len(result), 'Expect 1 contact in result')
        self.assertEquals('interactive_actor:responsible', result[0].token)
        self.assertEquals('interactive_actor:responsible', result[0].value)
        self.assertEquals('Responsible', result[0].title)

        result = self.source.search('Logged in')
        self.assertEquals(1, len(result), 'Expect 1 contact in result')
        self.assertEquals('interactive_actor:current_user', result[0].token)
        self.assertEquals('interactive_actor:current_user', result[0].value)
        self.assertEquals('Logged in user', result[0].title)


class TestTaskResponsibleSource(base.TestAllUsersInboxesAndTeamsSource):

    def setUp(self):
        super(TestTaskResponsibleSource, self).setUp()
        self.source = TaskResponsibleSource(self.portal)

    def test_interactive_users_are_valid(self):
        for actor_id in INTERACTIVE_ACTOR_IDS:
            self.assertIn(actor_id, self.source)

    def test_search_interactive_users(self):
        result = self.source.search('Resp')
        self.assertEquals(1, len(result), 'Expect 1 contact in result')
        self.assertEquals('interactive_actor:responsible', result[0].token)
        self.assertEquals('interactive_actor:responsible', result[0].value)
        self.assertEquals('Responsible', result[0].title)

        result = self.source.search('Logged in')
        self.assertEquals(1, len(result), 'Expect 1 contact in result')
        self.assertEquals('interactive_actor:current_user', result[0].token)
        self.assertEquals('interactive_actor:current_user', result[0].value)
        self.assertEquals('Logged in user', result[0].title)
