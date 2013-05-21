from opengever.testing import FunctionalTestCase
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.testing import create_contacts
from opengever.ogds.base.utils import create_session
from plone.app.testing import login, logout
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContentInContainer
from zope.component import getUtility
from zope.globalrequest import setRequest


class TestTransporter(FunctionalTestCase):

    def test_transporter(self):
        # Transporter tests
        # =================

        # We test the transporter using only one client since the setup is much
        # easier and the remote request are in fact a separate tool.

        request = self.layer.get('request')

        from opengever.testing import set_current_client_id
        set_current_client_id(self.portal)


        # Setup
        # -----

        # Set up a client for testing:

        session = create_session()

        _create_example_client(session, 'client1',
                                   {'title': 'Client 1',
                                    'ip_address': '127.0.0.1',
                                    'site_url': 'http://nohost/plone',
                                    'public_url': 'http://nohost/plone',
                                    'group': 'og_mandant2_users',
                                    'inbox_group': 'og_mandant2_inbox'})


        # FTI
        # ---

        # Create a default FTI which has a title and a description.

        fti = DexterityFTI('TransporterTestFTI',
                                klass="plone.dexterity.content.Container",
                                global_allow=True,
                                filter_content_types=False)
        fti.behaviors = ('plone.app.content.interfaces.INameFromTitle',)
        self.portal.portal_types._setObject('TransporterTestFTI', fti)
        schema = fti.lookupSchema()


        # Get the transporter utility:

        transporter = getUtility(ITransporter)

        # Popuate the request:

        setRequest(request)


        # Pulling a object
        # ----------------

        # Let's create a container first. We don't wanna test it on the plone site
        # since it's not dexterity.

        folder = createContentInContainer(self.portal, 'TransporterTestFTI',
                                               checkConstraints=False,
                                               title='Folder')

        # We need to create a dexterity object first.
        obj1 = createContentInContainer(folder, 'TransporterTestFTI',
                                             checkConstraints=False,
                                             title='Fo\xc3\xb6',
                                             description='Bar')
        self.assertEquals('Fo\xc3\xb6', obj1.title)
        self.assertEquals('Bar', obj1.description)

        # dublin core collector
        created = obj1.created()
        creator = obj1.Creator()

        # Pull the object:

        obj2 = transporter.transport_from(folder, 'client1', 'folder/foo')
        self.assertEquals('Fo\xc3\xb6', obj2.title)
        self.assertEquals('Bar', obj2.description)

        # dublin core collector
        self.assertEquals(obj2.created(), created)
        self.assertEquals(obj2.Creator(), creator)

        # Pushing a object
        # ----------------

        # Let's push obj2 back:

        data = transporter.transport_to(obj2, 'client1', 'folder')
        path3 = data['path'].encode('utf-8')
        self.assertEquals('folder/foo-2', path3)

        obj3 = self.portal.restrictedTraverse(path3)
        # obj3
        #     <Container at /plone/folder/foo-2>

        self.assertEquals('Fo\xc3\xb6', obj3.title)

        self.assertEquals('Bar', obj2.description)
