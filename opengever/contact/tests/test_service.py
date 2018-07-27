from ftw.builder import Builder
from ftw.builder import create
from opengever.contact import contact_service
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestContactService(FunctionalTestCase):

    def test_all_contact_brains_returns_brains_of_all_contacts(self):
        self.grant('Manager')

        lara = create(Builder('contact')
                      .having(firstname=u'Lara',
                              lastname=u'Croft',
                              email=u'lara.croft@test.ch'))

        superman = create(Builder('contact')
                          .having(firstname=u'Super',
                                  lastname=u'M\xe4n',
                                  email='superman@test.ch'))

        brains = contact_service().all_contact_brains()
        self.assertEquals(
            [lara, superman],
            [brain.getObject() for brain in brains])

    def test_all_contact_brains_ignores_security_by_default(self):
        self.grant('Authenticated')
        jamesbond = create(Builder('contact')
                           .having(firstname=u'James',
                                   lastname=u'Bond',
                                   email=None))

        jamesbond.__ac_local_roles_block__ = True
        jamesbond.reindexObjectSecurity()

        brains = contact_service().all_contact_brains()
        self.assertEquals(
            [(brain.firstname, brain.lastname) for brain in [jamesbond]],
            [(brain.firstname, brain.lastname) for brain in brains])

        brains = contact_service().all_contact_brains(ignore_security=False)
        self.assertEqual(0, len(brains))
