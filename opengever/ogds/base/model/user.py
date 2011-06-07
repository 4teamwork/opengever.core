from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, Boolean, Table
from zope.interface import implements
from opengever.ogds.base.interfaces import IUser
from opengever.ogds.base.interfaces import IClient
from sqlalchemy.orm import backref, relation
from sqlalchemy import ForeignKey

Base = declarative_base()


class User(Base):
    """User model
    """

    implements(IUser)

    __tablename__ = 'users'

    userid = Column(String(30), primary_key=True)
    active = Column(Boolean, default=True)
    firstname = Column(String(50))
    lastname = Column(String(50))

    directorate = Column(String(50))
    directorate_abbr = Column(String(10))
    department = Column(String(50))
    department_abbr = Column(String(10))

    email = Column(String(50))
    email2 = Column(String(50))
    url = Column(String(100))
    phone_office = Column(String(30))
    phone_fax = Column(String(30))
    phone_mobile = Column(String(30))

    salutation = Column(String(30))
    description = Column(Text())
    address1 = Column(String(100))
    address2 = Column(String(100))
    zip_code = Column(String(10))
    city = Column(String(100))

    country = Column(String(20))

    import_stamp = Column(String(26))

    def __init__(self, userid, **kwargs):
        self.userid = userid
        for key, value in kwargs.items():
            # provoke a AttributeError
            getattr(self, key)
            setattr(self, key, value)

    def __repr__(self):
        return '<User %s>' % self.userid


# association table
groups_users = Table('groups_users', Base.metadata,
    Column('groupid', String(30), ForeignKey('groups.groupid'), primary_key=True),
    Column('userid', String(30), ForeignKey('users.userid'), primary_key=True),
)


class Group(Base):
    """Group model, corresponds to a LDAP group
    """

    implements(IClient)

    __tablename__ = 'groups'

    groupid = Column(String(30), primary_key=True)
    title = Column(String(50))

    users = relation(User, secondary=groups_users, backref=backref('group_users'))

    def __init__(self, groupid, **kwargs):
        self.groupid = groupid

        for key, value in kwargs.items():
            # provoke a AttributeError
            getattr(self, key)
            setattr(self, key, value)

    def __repr__(self):
        return '<Group %s>' % self.groupid
