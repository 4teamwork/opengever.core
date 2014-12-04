from opengever.core.model import Base
from opengever.globalindex.oguid import Oguid
from opengever.meeting import _
from opengever.meeting.model.query import ProposalQuery
from opengever.ogds.base.utils import ogds_service
from plone import api
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import composite
from sqlalchemy.orm import relationship


class Proposal(Base):
    """Sql representation of a proposal."""

    query_cls = ProposalQuery

    __tablename__ = 'proposal'

    admin_unit_id = Column(String(30), primary_key=True)
    int_id = Column(Integer, primary_key=True, autoincrement=False)
    oguid = composite(Oguid, admin_unit_id, int_id)
    title = Column(String(256), nullable=False)
    physical_path = Column(String(256), nullable=False)
    workflow_state = Column(String(256), nullable=False)
    initial_position = Column(Text)

    commission_id = Column(Integer, ForeignKey('commissions.id'))
    commission = relationship('Commission', backref='proposals')

    def __repr__(self):
        return "<Proposal {}@{}>".format(self.int_id, self.admin_unit_id)

    def get_admin_unit(self):
        return ogds_service().fetch_admin_unit(self.admin_unit_id)

    @property
    def id(self):
        return self.proposal_id

    def get_searchable_text(self):
        searchable = filter(None, [self.title, self.initial_position])
        return ' '.join([term.encode('utf-8') for term in searchable])

    def get_link(self):
        admin_unit = self.get_admin_unit()
        url = '/'.join((admin_unit.public_url, self.physical_path))
        link = u'<a href="{0}" title="{1}">{1}</a>'.format(url, self.title)

        transformer = api.portal.get_tool('portal_transforms')
        return transformer.convertTo('text/x-html-safe', link).getData()

    def getPath(self):
        """This method is required by a tabbedview."""

        return self.physical_path
