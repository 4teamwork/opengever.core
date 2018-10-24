from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Meeting
from opengever.meeting.model import Proposal
from opengever.testing import IntegrationTestCase
from plone import api
from plone.app.testing import applyProfile


class TestHooks(IntegrationTestCase):

    features = ('meeting',)

    def test_execute_examplecontent_hooks(self):
        """Test that examplecontent hooks are executed successfully."""

        applyProfile(api.portal.get(), 'opengever.setup:default_content')
        applyProfile(api.portal.get(), 'opengever.examplecontent:empty_templates')
        applyProfile(api.portal.get(), 'opengever.examplecontent:repository_minimal')
        applyProfile(api.portal.get(), 'opengever.examplecontent:municipality_content')

        self.assertEqual(7, Proposal.query.count())
        self.assertEqual(4, AgendaItem.query.count())
        self.assertEqual(9, Meeting.query.count())
