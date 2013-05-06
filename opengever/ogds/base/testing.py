from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import setup_sql_tables
from opengever.core.testing import truncate_sql_tables
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.dexterity import utils


def create_contacts(portal):
    """Creates a bunch of contacts for testing with.
    """
    # create contact folder
    if 'contacts' not in portal.objectIds():
        contacts = utils.createContentInContainer(
            portal,
            'opengever.contact.contactfolder',
            checkConstraints=False,
            title='Contacts')
        assert 'contacts' in portal.objectIds(), \
            'Could not create contacts folder'
        contacts.reindexObject()
    else:
        contacts = portal.contacts

    contact_list = (
        ('Sandra', 'Kaufmann', 'sandra.kaufmann@test.ch'),
        ('Elisabeth', u'K\xe4ppeli'.encode('utf8'),
         'elisabeth.kaeppeli@test.ch'),
        ('Roger', 'Wermuth', None))

    for firstname, lastname, email in contact_list:
        obj = utils.createContentInContainer(
            contacts,
            'opengever.contact.contact',
            checkConstraints=False,
            firstname=firstname.decode('utf-8'),
            lastname=lastname.decode('utf-8'),
            email=email)
        obj.reindexObject()


class BaseLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FIXTURE, )

    def testSetUp(self):
        super(BaseLayer, self).testSetUp()
        setup_sql_tables()

    def testTearDown(self):
        super(BaseLayer, self).testTearDown()
        truncate_sql_tables()


OPENGEVER_OGDS_BASE_FIXTURE = BaseLayer()
OPENGEVER_OGDS_BASE_TESTING = IntegrationTesting(
    bases=(OPENGEVER_OGDS_BASE_FIXTURE,),
    name="OpengeverOgdsBase:Integration")
