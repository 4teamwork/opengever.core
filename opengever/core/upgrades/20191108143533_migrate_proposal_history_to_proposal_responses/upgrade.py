from ftw.upgrade import UpgradeStep
from opengever.base.response import IResponse
from opengever.base.response import ResponseContainer
from opengever.meeting.proposal import IBaseProposal
from opengever.meeting.proposalhistory import IProposalResponse
from opengever.meeting.proposalhistory import ProposalResponse
from zope.annotation.interfaces import IAnnotations
from zope.schema import getFields


annotation_key = 'object_history'


class MigrationResponseContainer(ResponseContainer):

    def add(self, response):
        """customized to avoid sending the ResponseAddedEvent, which would
        trigger response synchronization from submitted proposal to proposal
        as well as activities"""
        storage = self._storage(create_if_missing=True)
        if not IResponse.providedBy(response):
            raise ValueError('Only Response objects are allowed to add')

        response_id = self._generate_response_id(response.created, storage)

        response.response_id = response_id
        storage[response_id] = response
        return response_id


class MigrateProposalHistoryToProposalResponses(UpgradeStep):
    """Migrate proposal history to proposal responses.
    """

    deferrable = True

    def __call__(self):
        for proposal in self.objects(
                {'object_provides': IBaseProposal.__identifier__},
                'Migrate proposal history to proposal responses.'):
            self.migrate_records_to_responses(proposal)

    def migrate_records_to_responses(self, context):
        fields = getFields(IProposalResponse)

        history = IAnnotations(context).get(annotation_key, None)
        if history is None:
            return

        response_container = MigrationResponseContainer(context)

        for key, record in history.items():
            created = record.pop('created')
            history_type = record.pop('history_type')
            userid = record.pop('userid')
            text = record.pop('text')

            # we do not need the uuid
            record.pop('uuid')

            response = ProposalResponse(history_type, text=text, **record)
            response.creator = fields['creator']._type(userid)
            assert(isinstance(created, fields['created']._type))
            response.created = created.replace(microsecond=0)

            response_container.add(response)
