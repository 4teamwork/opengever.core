from datetime import datetime
from opengever.base.model import Base
from opengever.meeting import _
from opengever.ogds.base.actor import Actor
from plone import api
from sqlalchemy import Column
from sqlalchemy import DateTime
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
    created = Column(DateTime, default=datetime.now, nullable=False)
    userid = Column(String(256), default=get_current_user_id, nullable=False)

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
