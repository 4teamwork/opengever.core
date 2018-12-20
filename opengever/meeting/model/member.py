from opengever.base.model import Base
from opengever.base.model import EMAIL_LENGTH
from opengever.base.model import FIRSTNAME_LENGTH
from opengever.base.model import LASTNAME_LENGTH
from opengever.base.model import SQLFormSupport
from opengever.base.utils import escape_html
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import column_property
from sqlalchemy.schema import Sequence


class Member(Base, SQLFormSupport):

    __tablename__ = 'members'

    member_id = Column("id", Integer, Sequence("member_id_seq"),
                       primary_key=True)
    firstname = Column(String(FIRSTNAME_LENGTH), nullable=False)
    lastname = Column(String(LASTNAME_LENGTH), nullable=False)
    fullname = column_property(lastname + " " + firstname)
    email = Column(String(EMAIL_LENGTH))

    def __repr__(self):
        return '<Member {}>'.format(repr(self.fullname))

    @property
    def css_class(self):
        return 'contenttype-opengever-meeting-member'

    def get_link(self, context, title=None):
        title = title or self.fullname
        url = self.get_url(context)
        link = u'<a href="{0}" title="{1}" class="{2}">{1}</a>'.format(
            url, escape_html(title), self.css_class)
        return link

    def get_firstname_link(self, context):
        return self.get_link(context, title=self.firstname)

    def get_lastname_link(self, context):
        return self.get_link(context, title=self.lastname)

    def get_url(self, context, view=None):
        elements = [context.absolute_url(), "member-{}".format(self.member_id)]
        if view:
            elements.append(view)

        return '/'.join(elements)

    def get_title(self, show_email_as_link=True):
        fullname = escape_html(self.fullname)
        email = escape_html(self.email)

        if not email:
            return fullname

        if show_email_as_link:
            email = u'<a href="mailto:{email}">{email}</a>'.format(email=email)

        participant = u'{} ({})'.format(fullname, email)

        return participant
