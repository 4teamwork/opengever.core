from ftw.builder import session
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Meeting
from opengever.meeting.model import Proposal
from opengever.testing import IntegrationTestCase
from plone import api
from plone.app.testing import applyProfile


class TestHooks(IntegrationTestCase):

    features = ('meeting', 'word-meeting')

    def test_execute_examplecontent_hooks(self):
        """Test that examplecontent hooks are executed successfully."""

        applyProfile(api.portal.get(), 'opengever.setup:default_content')
        applyProfile(api.portal.get(), 'opengever.examplecontent:empty_templates')
        applyProfile(api.portal.get(), 'opengever.examplecontent:repository_minimal')
        applyProfile(api.portal.get(), 'opengever.examplecontent:municipality_content')
        applyProfile(api.portal.get(), 'opengever.examplecontent:init')

        self.assertEqual(11, Proposal.query.count())
        self.assertEqual(8, AgendaItem.query.count())
        self.assertEqual(13, Meeting.query.count())
