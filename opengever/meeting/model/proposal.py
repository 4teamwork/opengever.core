from opengever.core.model import Base
from opengever.globalindex.oguid import Oguid
from opengever.meeting import _
from opengever.meeting.model.query import ProposalQuery
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import composite
from sqlalchemy.schema import Sequence
from zope import schema
from zope.interface import Interface


class IProposalModel(Interface):

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        description=_('help_title', default=u""),
        required=True,
        max_length=256,
        )

    initial_position = schema.Text(
        title=_('label_initial_position', default=u"Proposal"),
        description=_("help_initial_position", default=u""),
        required=False,
        )


class Proposal(Base):
    """Sql representation of a proposal."""

    query_cls = ProposalQuery

    __tablename__ = 'proposal'
    proposal_id = Column("id", Integer, Sequence("proposal_id_seq"),
                         primary_key=True)

    admin_unit_id = Column(String(30), index=True, nullable=False)
    int_id = Column(Integer, index=True, nullable=False)
    oguid = composite(Oguid, admin_unit_id, int_id)

    title = Column(String(256))
    initial_position = Column(Text)

    def __repr__(self):
        return "<Proposal {}@{}>".format(self.int_id, self.admin_unit_id)

    @property
    def id(self):
        return self.proposal_id

    def get_searchable_text(self):
        searchable = filter(None, [self.title, self.initial_position])
        return ''.join([term.encode('utf-8') for term in searchable])
