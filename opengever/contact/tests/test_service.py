from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.service import ContactService
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from plone.app.testing import TEST_USER_ID


class TestContactService(FunctionalTestCase):

    def test_all_contacts_returns_brains_of_all_contacts(self):
        self.grant('Manager')

        lara = create(Builder('contact')
                      .having(firstname=u'Lara',
                              lastname=u'Croft',
                              email=u'lara.croft@test.ch'))

        superman = create(Builder('contact')
                          .having(firstname=u'Super',
                                  lastname=u'M\xe4n',
                                  email='superman@test.ch'))

        brains = ContactService().all_contacts()
        self.assertEquals(
            [lara, superman],
            [brain.getObject() for brain in brains])

    def test_all_contacts_ignores_security_by_default(self):
        jamesbond = create(Builder('contact')
                           .having(**{'firstname': u'James',
                                      'lastname': u'Bond',
                                      'email': None}))
        jamesbond.manage_delLocalRoles(TEST_USER_ID)

        brains = ContactService().all_contacts()
        self.assertEquals(
            [(brain.firstname, brain.lastname) for brain in [jamesbond]],
            [(brain.firstname, brain.lastname) for brain in brains])

        brains = ContactService().all_contacts(ignore_security=False)
        self.assertEqual(0, len(brains))
