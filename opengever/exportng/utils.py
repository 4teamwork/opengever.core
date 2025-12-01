from Acquisition import aq_parent
from collections import namedtuple
from opengever.ogds.models.service import ogds_service

CACHE = {}

Attribute = namedtuple(
    'Attribute',
    ['name', 'col_name', 'col_type'],
)


def userid_to_email(userid):
    userid_email_mapping = CACHE.get('userid_email_mapping', None)
    if userid_email_mapping is None:
        users = ogds_service().all_users()
        userid_email_mapping = {}
        for user in users:
            if user.email:
                userid_email_mapping[user.userid] = user.email
                if user.userid != user.username:
                    userid_email_mapping[user.username] = user.email
        CACHE['userid_email_mapping'] = userid_email_mapping
    return userid_email_mapping.get(userid, userid)


def document_parent(doc):
    parent = aq_parent(doc)
    # Proposal documents are stored in the dossier containing the proposal
    if parent.portal_type == 'opengever.meeting.proposal':
        parent = aq_parent(parent)
    elif parent.portal_type == 'opengever.meeting.submittedproposal':
        proposal = parent.load_model()
        # Documents of a scheduled proposal are stored in the agenda item
        if proposal.agenda_item is not None:
            return proposal.agenda_item
        # Documents of a submitted proposal are stored in the proposal
        else:
            parent = proposal.resolve_submitted_proposal() or proposal.resolve_proposal()
    else:
        # Documents in tasks are added to the dossier
        while parent.portal_type == 'opengever.task.task':
            parent = aq_parent(parent)
    return parent
