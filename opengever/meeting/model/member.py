from opengever.base.model import Base
from plone import api
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import column_property
from sqlalchemy.schema import Sequence


class Member(Base):

    __tablename__ = 'members'

    member_id = Column("id", Integer, Sequence("member_id_seq"),
                       primary_key=True)
    firstname = Column(String(256), nullable=False)
    lastname = Column(String(256), nullable=False)
    fullname = column_property(firstname + " " + lastname)
    email = Column(String(256))

    def __repr__(self):
        return '<Member {}>'.format(repr(self.fullname))

    def get_link(self, context, title=None):
        title = title or self.fullname
        url = self.get_url(context)
        link = u'<a href="{0}" title="{1}">{1}</a>'.format(url, title)

        transformer = api.portal.get_tool('portal_transforms')
        return transformer.convertTo('text/x-html-safe', link).getData()

    def get_firstname_link(self, context):
        return self.get_link(context, title=self.firstname)

    def get_lastname_link(self, context):
        return self.get_link(context, title=self.lastname)

    def get_url(self, context):
        return "{}/member/{}".format(context.absolute_url(), self.member_id)

    def get_edit_url(self, context):
        return '/'.join((self.get_url(context), 'edit'))

    def get_breadcrumbs(self, context):
        return {'absolute_url': self.get_url(context), 'Title': self.fullname}

    def get_edit_values(self, fieldnames):
        values = {}
        for fieldname in fieldnames:
            value = getattr(self, fieldname, None)
            if not value:
                continue

            values[fieldname] = value
        return values

    def update_model(self, data):
        for key, value in data.items():
            setattr(self, key, value)
