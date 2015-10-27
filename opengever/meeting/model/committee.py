from opengever.base.model import Base
from opengever.base.oguid import Oguid
from opengever.base.utils import escape_html
from opengever.ogds.base.utils import ogds_service
from opengever.ogds.models import GROUP_ID_LENGTH
from opengever.ogds.models import UNIT_ID_LENGTH
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import composite
from sqlalchemy.schema import Sequence


class Committee(Base):

    __tablename__ = 'committees'
    __table_args__ = (UniqueConstraint('admin_unit_id', 'int_id'), {})

    committee_id = Column("id", Integer, Sequence("committee_id_seq"),
                          primary_key=True)

    group_id = Column(String(GROUP_ID_LENGTH),
                      nullable=False)

    admin_unit_id = Column(String(UNIT_ID_LENGTH), nullable=False)
    int_id = Column(Integer, nullable=False)
    oguid = composite(Oguid, admin_unit_id, int_id)
    title = Column(String(256))
    physical_path = Column(String(256), nullable=False)

    def __repr__(self):
        return '<Committee {}>'.format(repr(self.title))

    def get_admin_unit(self):
        return ogds_service().fetch_admin_unit(self.admin_unit_id)

    def get_link(self):
        url = self.get_url()
        if not url:
            return ''

        link = u'<a href="{0}" title="{1}">{1}</a>'.format(
            url, escape_html(self.title))
        return link

    def get_url(self, admin_unit=None):
        admin_unit = admin_unit or self.get_admin_unit()
        if not admin_unit:
            return None

        return '/'.join((admin_unit.public_url, self.physical_path))

    def resolve_committee(self):
        return self.oguid.resolve_object()

    def get_protocol_template(self):
        return self.resolve_committee().get_protocol_template()

    def get_excerpt_template(self):
        return self.resolve_committee().get_excerpt_template()
