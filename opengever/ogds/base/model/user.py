from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, Boolean
from zope.interface import implements
from opengever.ogds.base.interfaces import IUser


Base = declarative_base()


class User(Base):
    """User model
    """

    implements(IUser)

    __tablename__ = 'users'

    userid = Column(String(10), primary_key=True)
    active = Column(Boolean, default=True)
    firstname = Column(String(50))
    lastname = Column(String(50))

    directorate = Column(String(30))
    directorate_abbr = Column(String(10))
    department = Column(String(30))
    department_abbr = Column(String(10))

    email = Column(String(50))
    email2 = Column(String(50))
    url = Column(String(100))
    phone_office = Column(String(30))
    phone_fax = Column(String(30))
    phone_mobile = Column(String(30))

    salutation = Column(String(30))
    description = Column(Text())
    address1 = Column(String(30))
    address2 = Column(String(30))
    zip_code = Column(String(10))
    city = Column(String(100))

    country = Column(String(20))

    def __init__(self, userid):
        self.userid = userid

    def __repr__(self):
        return '<User %s>' % self.userid
