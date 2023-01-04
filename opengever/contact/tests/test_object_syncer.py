from opengever.base.model import create_session
from opengever.contact.models import Person
from opengever.contact.syncer.object_syncer import PersonSyncer
from opengever.testing import FunctionalTestCase
from path import Path
from pkg_resources import resource_string
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy.orm import sessionmaker
import os


assets = Path('{}/assets/object_syncer/'.format(os.path.dirname(__file__)))


def load_asset(name):
    return resource_string('opengever.contact.tests',
                           'assets/object_syncer/{}'.format(name))


class SyncerBaseTest(FunctionalTestCase):

    SAMPLE_DATA = []

    def setUp(self):
        super(SyncerBaseTest, self).setUp()
        self.session = create_session()

        engine = create_engine('sqlite:///:memory:')
        self.source_db = sessionmaker(bind=engine)()
        self.source_metadata = MetaData(engine)
        self.create_source_db()
        self.insert_sample_data()

    def create_source_db(self):
        raise NotImplementedError

    def insert_sample_data(self):
        for item in self.SAMPLE_DATA:
            self.source_db.execute(
                self.source_table.insert().values(**item))

    def tearDown(self):
        super(SyncerBaseTest, self).tearDown()
        self.session.close()


class TestPersonSyncer(SyncerBaseTest):

    SAMPLE_DATA = [{u'is_active': True, u'former_contact_id': 1,
                    u'firstname': u'Frank G.', u'lastname': u'Dippel',
                    u'salutation': u'Herr', u'title': u'Dr.',
                    u'description': u'Lorem ipsum'},
                   {u'is_active': False, u'former_contact_id': 2,
                    u'firstname': u'Christiane',
                    u'lastname': u'W\xfcrsd\xf6rfer',
                    u'description': u'Bla',
                    u'salutation': u'Frau', u'title': u'B.Sc.'},
                   {u'is_active': True, u'former_contact_id': 3,
                    u'firstname': u'Dolorene', u'lastname': u'Dolores',
                    u'salutation': u'Frau', u'title': u'',
                    u'description': u'Lorem ipsum sit'}]

    def create_source_db(self):
        self.source_table = Table("persons",
                                  self.source_metadata,
                                  Column("former_contact_id", Integer),
                                  Column("salutation", String),
                                  Column("title", String),
                                  Column("firstname", String),
                                  Column("lastname", String),
                                  Column("description", Text),
                                  Column("is_active", Boolean))
        self.source_table.create()

    def test_add_objects_properly_while_syncing(self):
        syncer = PersonSyncer(self.source_db, 'SELECT * from persons')
        syncer()

        self.assertEqual(3, len(Person.query.all()))

        person = Person.query.get_by_former_contact_id(2)
        self.assertItemsEqual(
            [u'Frau', u'B.Sc.', u'Christiane',
             u'W\xfcrsd\xf6rfer', False, 2, u'Bla'],
            [person.salutation, person.academic_title, person.firstname,
             person.lastname, person.is_active, person.former_contact_id,
             person.description])

        person = Person.query.get_by_former_contact_id(1)
        self.assertItemsEqual(
            [u'Herr', u'Dr.', u'Frank G.', u'Dippel', True, u'Lorem ipsum'],
            [person.salutation, person.academic_title, person.firstname,
             person.lastname, person.is_active, person.description])

    def test_update_object_properly_while_syncing(self):
        syncer = PersonSyncer(self.source_db, 'SELECT * from persons')
        syncer()

        self.assertEqual(3, len(Person.query.all()))

        self.source_db.execute(
            self.source_table.update().where(
                self.source_table.c.former_contact_id == 3).values(
                    lastname=u'Meier', is_active=False, description=u''))

        PersonSyncer(self.source_db, 'SELECT * from persons')()

        self.assertEqual(3, len(Person.query.all()))
        person = Person.query.get_by_former_contact_id(3)
        self.assertEquals('Meier', person.lastname)
        self.assertEquals('', person.description)
        self.assertFalse(person.is_active)
