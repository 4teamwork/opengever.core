from opengever.ogds.base.interfaces import IClient
from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from zope.interface import implements


Base = declarative_base()


class Client(Base):
    """Client model
    """

    implements(IClient)

    __tablename__ = 'clients'

    client_id = Column(String(10), primary_key=True)
    enabled = Column(Boolean())
    ip_address = Column(String(15))
    site_url = Column(String(50))
    public_url = Column(String(50))
    group = Column(String(20))
    inbox_group = Column(String(20))

    def __init__(self, client_id):
        self.client_id = client_id

    def __repr__(self):
        return '<Client %s>' % self.client_id
