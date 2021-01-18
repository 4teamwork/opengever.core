from opengever.tasktemplates.sources import TaskResponsibleSource
from opengever.tasktemplates.sources import TaskTemplateIssuerSource
from opengever.ogds.base.tests import test_sources as base


class TestTaskTemplateIssuerSource(base.TestUsersContactsInboxesSource):

    def setUp(self):
        super(TestTaskTemplateIssuerSource, self).setUp()
        self.source = TaskResponsibleSource(self.portal)

        self.source = TaskTemplateIssuerSource(self.portal)

    def test_interactive_users_are_valid(self):
        self.assertIn('current_user', self.source)
        self.assertIn('responsible', self.source)

    def test_search_interactive_users(self):
        result = self.source.search('Resp')
        self.assertEquals(1, len(result), 'Expect 1 contact in result')
        self.assertEquals('responsible', result[0].token)
        self.assertEquals('responsible', result[0].value)
        self.assertEquals('Responsible', result[0].title)

        result = self.source.search('Logged in')
        self.assertEquals(1, len(result), 'Expect 1 contact in result')
        self.assertEquals('current_user', result[0].token)
        self.assertEquals('current_user', result[0].value)
        self.assertEquals('Logged in user', result[0].title)


class TestTaskResponsibleSource(base.TestAllUsersInboxesAndTeamsSource):

    def setUp(self):
        super(TestTaskResponsibleSource, self).setUp()
        self.source = TaskResponsibleSource(self.portal)

    def test_interactive_users_are_valid(self):
        self.assertIn('interactive_users:current_user', self.source)
        self.assertIn('interactive_users:responsible', self.source)

    def test_search_interactive_users(self):
        result = self.source.search('Resp')
        self.assertEquals(1, len(result), 'Expect 1 contact in result')
        self.assertEquals('interactive_users:responsible', result[0].token)
        self.assertEquals('interactive_users:responsible', result[0].value)
        self.assertEquals('Responsible', result[0].title)

        result = self.source.search('Logged in')
        self.assertEquals(1, len(result), 'Expect 1 contact in result')
        self.assertEquals('interactive_users:current_user', result[0].token)
        self.assertEquals('interactive_users:current_user', result[0].value)
        self.assertEquals('Logged in user', result[0].title)
