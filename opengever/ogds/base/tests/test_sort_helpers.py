from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.sort_helpers import SortHelpers
from opengever.testing import FunctionalTestCase


class TestUserSortDict(FunctionalTestCase):

    def setUp(self):
        super(TestUserSortDict, self).setUp()
        self.grant('Contributor', 'Reader')

        create(Builder('org_unit')
               .id('arch')
               .having(admin_unit=self.admin_unit)
               .having(title=u'Landesarchiv'))

        self.hugo = create(Builder('ogds_user')
                           .id(u'hugo.boss')
                           .having(firstname=u'Hugo', lastname=u'Boss'))

        self.albert = create(Builder('ogds_user')
                             .id(u'albert.peter')
                             .having(firstname=u'Albert', lastname=u'Peter'))

        self.james = create(Builder('ogds_user')
                            .id(u'james.bond')
                            .having(firstname=u'James', lastname=u'Bond'))

    def test_user_sort_dict_returns_a_dict_with_userid_as_key_fullname_as_value_includings_inboxes(self):
        self.assertEqual(
            {u'albert.peter': u'Peter Albert',
             u'test_user_1_': u'Test User',
             u'inbox:org-unit-1': u'Inbox: Org Unit 1',
             u'inbox:arch': u'Inbox: Landesarchiv',
             u'hugo.boss': u'Boss Hugo',
             u'james.bond': u'Bond James'},
            SortHelpers().get_user_sort_dict())

    def test_user_contact_sort_dict_extend_sort_dict_with_all_contacts(self):
        create(Builder('contact')
               .having(firstname=u'Lara',
                       lastname=u'Croft',
                       email=u'lara.croft@example.com'))

        create(Builder('contact')
               .having(firstname=u'Super',
                       lastname=u'M\xe4n',
                       email='superman@example.com'))

        self.assertEqual(
            {u'albert.peter': u'Peter Albert',
             u'contact:croft-lara': u'Croft Lara',
             u'contact:man-super': u'M\xe4n Super',
             u'test_user_1_': u'Test User',
             u'inbox:org-unit-1': u'Inbox: Org Unit 1',
             u'inbox:arch': u'Inbox: Landesarchiv',
             u'hugo.boss': u'Boss Hugo',
             u'james.bond': u'Bond James'},
            SortHelpers().get_user_contact_sort_dict())

    def test_user_contact_sort_dict_is_not_none_for_emtpy_contacts(self):
        self.assertIsNotNone(SortHelpers().get_user_contact_sort_dict())
        self.assertEqual(
            {u'albert.peter': u'Peter Albert',
             u'test_user_1_': u'Test User',
             u'inbox:org-unit-1': u'Inbox: Org Unit 1',
             u'inbox:arch': u'Inbox: Landesarchiv',
             u'hugo.boss': u'Boss Hugo',
             u'james.bond': u'Bond James'},
            SortHelpers().get_user_contact_sort_dict())
