from opengever.base.request import dispatch_json_request
from opengever.base.transport import REQUEST_KEY
from opengever.base.transport import Transporter
import json


class CreateSubmittedProposalCommand(object):

    def __init__(self, proposal):
        self.proposal = proposal
        self.submitted_proposal_path = None
        self.admin_unit_id = self.proposal.get_committee_admin_unit().id()

    def execute(self):
        model = self.proposal.load_model()
        jsondata = {'committee_oguid': model.committee.oguid.id,
                    'proposal_oguid': model.oguid.id}
        request_data = {REQUEST_KEY: json.dumps(jsondata)}
        response = dispatch_json_request(
            self.admin_unit_id, '@@create_submitted_proposal', data=request_data)
        self.submitted_proposal_path = response['path']


class CopyProposalDocumentCommand(object):

    def __init__(self, document, parent_action):
        self.document = document
        self.parent_action = parent_action

    def execute(self):
        assert self.parent_action.submitted_proposal_path
        target = self.parent_action.submitted_proposal_path
        OgCopyCommand(self.document, self.parent_action.admin_unit_id, target).run()


class OgCopyCommand(object):

    def __init__(self, source, target_admin_unit_id, target_path):
        self.source = source
        self.target_path = target_path
        self.target_admin_unit_id = target_admin_unit_id

    def run(self):
        Transporter().transport_to(
            self.source, self.target_admin_unit_id, self.target_path)
