from opengever.meeting.connector.connector import Connector
from opengever.meeting.connector.connector import ConnectorAction
from opengever.meeting.connector.connector import ConnectorPath
from opengever.testing import IntegrationTestCase


@Connector.register
class DummyConnectorAction(ConnectorAction):
    recorder = []  # only for testing. records the execution

    def execute(self):
        self.recorder.append({
            'id': self.context.getId(),
            'data': self.data})


class TestConnector(IntegrationTestCase):
    features = ('meeting',)

    def setUp(self):
        super(TestConnector, self).setUp()
        DummyConnectorAction.recorder = []

    def test_dispatch_action_executes_action_for_each_connected_path(self):
        self.login(self.committee_responsible)
        self.connector.dispatch(DummyConnectorAction)

        recorded = DummyConnectorAction.recorder

        self.assertItemsEqual(
            [self.proposal.getId(), self.submitted_proposal.getId()],
            [item.get('id') for item in recorded]
            )

    def test_dispatch_action_passes_the_data_to_the_action(self):
        self.login(self.committee_responsible)
        text = u'james b\xc3\xb6nd'
        values = [1, 2, 3]

        self.connector.dispatch(DummyConnectorAction, text=text, values=values)

        self.assertDictEqual(
            {'text': text, 'values': values},
            DummyConnectorAction.recorder[0].get('data'))

    @property
    def connector(self):
        connector = Connector()
        proposal_path = ConnectorPath(
            self.proposal.get_sync_admin_unit_id(),
            self.proposal.get_sync_target_path())

        connector.connect_path(proposal_path)

        submitted_proposal_path = ConnectorPath(
            self.submitted_proposal.get_sync_admin_unit_id(),
            self.submitted_proposal.get_sync_target_path())

        connector.connect_path(submitted_proposal_path)
        return connector


class TestProposalConnector(IntegrationTestCase):
    features = ('meeting',)

    def setUp(self):
        super(TestProposalConnector, self).setUp()
        DummyConnectorAction.recorder = []

    def test_sql_proposal_connector_connects_its_proposal_and_submitted_proposal(self):
        self.login(self.committee_responsible)

        connector = self.proposal.load_model().connector
        connector.dispatch(DummyConnectorAction)

        recorded = DummyConnectorAction.recorder

        self.assertItemsEqual(
            [self.proposal.getId(), self.submitted_proposal.getId()],
            [item.get('id') for item in recorded]
            )
