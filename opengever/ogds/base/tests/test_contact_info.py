from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_org_unit
from opengever.testing import create_and_select_current_org_unit
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from opengever.testing import FunctionalTestCase
from opengever.testing import select_current_org_unit
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility


class TestClientUtils(FunctionalTestCase):

    def setUp(self):
        super(TestClientUtils, self).setUp()
        self.test_ou = create_and_select_current_org_unit('test_client')

    def test_get_current_org_unit(self):
        self.assertEquals(u'test_client', get_current_org_unit().id())


class TestClientHelpers(FunctionalTestCase):
    use_default_fixture = False

    def setUp(self):
        super(TestClientHelpers, self).setUp()
        self.info = getUtility(IContactInformation)

        self.client1 = create_client(clientid='client1')
        self.client2 = create_client(clientid='client2')
        create_client(clientid='client3', enabled=False)

        create_ogds_user(TEST_USER_ID, assigned_client=[self.client1],
                 firstname="Test", lastname="User")
        select_current_org_unit('client1')


class TestContactInfoAdditionals(FunctionalTestCase):
    use_default_fixture = False

    def setUp(self):
        super(TestContactInfoAdditionals, self).setUp()
        create(Builder('fixture').with_admin_unit())
        self.info = getUtility(IContactInformation)

    def test_contacts_or_inboxes_is_not_a_user(self):
        self.assertFalse(self.info.is_user(u'inbox:client1'))
        self.assertFalse(self.info.is_user(u'contact:croft-lara'))

    def test_all_possibly_valid_userids_are_a_user(self):
        self.assertTrue(self.info.is_user('hugo.boss'))
        self.assertTrue(self.info.is_user('peter.muster'))
