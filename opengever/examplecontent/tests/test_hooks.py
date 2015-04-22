from ftw.builder import session
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Meeting
from opengever.meeting.model import Proposal
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import applyProfile


class TestHooks(FunctionalTestCase):

    def setUp(self):
        super(TestHooks, self).setUp()
        # session will be changed by the executed hook, backup
        self._builder_session = session.current_session

    def tearDown(self):
        # restore session
        session.current_session = self._builder_session
        super(TestHooks, self).tearDown()

    def test_execute_examplecontent_hooks(self):
        """Test that examplecontent hooks are executed successfully."""

        applyProfile(api.portal.get(), 'opengever.setup:default_content')
        applyProfile(api.portal.get(), 'opengever.setup:empty_templates')
        applyProfile(api.portal.get(), 'opengever.examplecontent:repository_minimal')
        applyProfile(api.portal.get(), 'opengever.examplecontent:municipality_content')
        applyProfile(api.portal.get(), 'opengever.examplecontent:init')

        self.assertEqual(4, Proposal.query.count())
        self.assertEqual(4, AgendaItem.query.count())
        self.assertEqual(5, Meeting.query.count())
