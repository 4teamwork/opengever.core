from opengever.base.model import create_session
from opengever.tabbedview.sqlsource import sort_column_exists
from opengever.testing import FunctionalTestCase
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import aliased
from sqlalchemy.orm import relationship


Base = declarative_base()


class Something(Base):
    __tablename__ = 'something'

    some_id = Column(Integer, primary_key=True)
    some_string = Column(String)
    some_entity = Column(Integer, ForeignKey('somethong.some_id'))


class Somethong(Base):
    __tablename__ = 'somethong'

    some_id = Column(Integer, primary_key=True)
    some_thing = relationship('Something', backref='some_aliases')


class TestSortColumnExists(FunctionalTestCase):

    def setUp(self):
        super(TestSortColumnExists, self).setUp()
        self.session = create_session()

    def test_sorting_by_column(self):
        query = self.session.query(Something)
        self.assertTrue(sort_column_exists(query, 'some_string'))

    def test_sorting_by_entity(self):
        query = self.session.query(Something)
        self.assertTrue(sort_column_exists(query, 'some_entity'))

    def test_sorting_by_alias(self):
        query = self.session.query(Something,
                                   aliased(Something, name='some_alias'))
        self.assertTrue(sort_column_exists(query, 'some_alias'))
