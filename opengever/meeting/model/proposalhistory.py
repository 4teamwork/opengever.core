from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import Base
from opengever.base.model import UTCDateTime
from opengever.meeting import _
from opengever.ogds.base.actor import Actor
from opengever.ogds.models import USER_ID_LENGTH
from opengever.ogds.models.types import UnicodeCoercingText
from plone import api
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


def get_current_user_id():
    return api.user.get_current().getId()


class ProposalHistory(Base):

    css_class = None

    __tablename__ = 'proposalhistory'

    proposal_history_record_id = Column(
        "id", Integer,
        Sequence("proposal_history_id_seq"), primary_key=True)
    proposal_id = Column(Integer, ForeignKey('proposals.id'), nullable=False)
    proposal = relationship('Proposal')
    created = Column(UTCDateTime(timezone=True), default=utcnow_tz_aware, nullable=False)
    userid = Column(String(USER_ID_LENGTH), default=get_current_user_id, nullable=False)
    text = Column(UnicodeCoercingText)

    # intended to be used only by DocumentSubmitted/DocumentUpdated
    submitted_document_id = Column(Integer, ForeignKey('submitteddocuments.id'))
    submitted_document = relationship("SubmittedDocument")
    document_title = Column(String(256))
    submitted_version = Column(Integer)

    # intended to be used only by Scheduled
    meeting_id = Column(Integer, ForeignKey('meetings.id'))
    meeting = relationship("Meeting")

    proposal_history_type = Column(String(100), nullable=False)
    __mapper_args__ = {'polymorphic_on': proposal_history_type}

    def message(self):
        raise NotImplementedError()

    def get_actor_link(self):
        return Actor.lookup(self.userid).get_link()


class Created(ProposalHistory):

    __mapper_args__ = {'polymorphic_identity': 'created'}

    css_class = 'created'

    def message(self):
        return _(u'proposal_history_label_created',
                 u'Created by ${user}',
                 mapping={'user': self.get_actor_link()})


class Submitted(ProposalHistory):

    __mapper_args__ = {'polymorphic_identity': 'submitted'}

    css_class = 'submitted'

    def message(self):
        return _(u'proposal_history_label_submitted',
                 u'Submitted by ${user}',
                 mapping={'user': self.get_actor_link()})


class Rejected(ProposalHistory):

    __mapper_args__ = {'polymorphic_identity': 'rejected'}

    css_class = 'rejected'

    def message(self):
        return _(u'proposal_history_label_rejected',
                 u'Rejected by ${user}',
                 mapping={'user': self.get_actor_link()})


class Scheduled(ProposalHistory):

    __mapper_args__ = {'polymorphic_identity': 'scheduled'}

    css_class = 'scheduled'

    def message(self):
        meeting_title = self.meeting.get_title() if self.meeting else u''
        return _(u'proposal_history_label_scheduled',
                 u'Scheduled for meeting ${meeting} by ${user}',
                 mapping={'user': self.get_actor_link(),
                          'meeting': meeting_title})


class RemoveScheduled(ProposalHistory):

    __mapper_args__ = {'polymorphic_identity': 'removescheduled'}

    css_class = 'scheduleRemoved'

    def message(self):
        meeting_title = self.meeting.get_title() if self.meeting else u''
        return _(u'proposal_history_label_remove_scheduled',
                 u'Removed from schedule of meeting ${meeting} by ${user}',
                 mapping={'user': self.get_actor_link(),
                          'meeting': meeting_title})


class DocumentSubmitted(ProposalHistory):

    __mapper_args__ = {'polymorphic_identity': 'documentsubmitted'}

    css_class = 'documentAdded'

    def message(self):
        return _(u'proposal_history_label_document_submitted',
                 u'Document ${title} submitted in version ${version} by ${user}',
                 mapping={'user': self.get_actor_link(),
                          'title': self.document_title or '',
                          'version': self.submitted_version})


class DocumentUpdated(ProposalHistory):

    __mapper_args__ = {'polymorphic_identity': 'documentupdated'}

    css_class = 'documentUpdated'

    def message(self):
        return _(u'proposal_history_label_document_updated',
                 u'Submitted document ${title} updated to version ${version} by ${user}',
                 mapping={'user': self.get_actor_link(),
                          'title': self.document_title or '',
                          'version': self.submitted_version})


class ProposalDecided(ProposalHistory):

    __mapper_args__ = {'polymorphic_identity': 'decided'}

    css_class = 'decided'

    def message(self):
        return _(u'proposal_history_label_decided',
                 u'Proposal decided by ${user}',
                 mapping={'user': self.get_actor_link()})


class ProposalReopened(ProposalHistory):

    __mapper_args__ = {'polymorphic_identity': 'reopened'}

    css_class = 'reopened'

    def message(self):
        return _(u'proposal_history_label_reopened',
                 u'Proposal reopened by ${user}',
                 mapping={'user': self.get_actor_link()})


class ProposalRevised(ProposalHistory):

    __mapper_args__ = {'polymorphic_identity': 'revised'}

    css_class = 'revised'

    def message(self):
        return _(u'proposal_history_label_revised',
                 u'Proposal revised by ${user}',
                 mapping={'user': self.get_actor_link()})


class Cancelled(ProposalHistory):

    __mapper_args__ = {'polymorphic_identity': 'cancelled'}

    css_class = 'cancelled'

    def message(self):
        return _(u'proposal_history_label_cancelled',
                 u'Proposal cancelled by ${user}',
                 mapping={'user': self.get_actor_link()})


class Reactivated(ProposalHistory):

    __mapper_args__ = {'polymorphic_identity': 'reactivated'}

    css_class = 'reactivated'

    def message(self):
        return _(u'proposal_history_label_reactivated',
                 u'Proposal reactivated by ${user}',
                 mapping={'user': self.get_actor_link()})
