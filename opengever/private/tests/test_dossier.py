from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility


class TestPrivateDossier(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER

    def setUp(self):
        super(TestPrivateDossier, self).setUp()
        self.root = create(Builder('private_root'))
        self.folder = create(Builder('private_folder')
                             .having(userid=TEST_USER_ID)
                             .within(self.root))

    @browsing
    def test_is_addable_to_a_private_folder(self, browser):
        browser.login().open(self.folder)
        factoriesmenu.add('Private Dossier')
        browser.fill({'Title': u'My Personal Stuff',
                      'Responsible': TEST_USER_ID})
        browser.click_on('Save')

        self.assertEquals([u'My Personal Stuff'], browser.css('h1').text)

    def test_use_same_id_schema_as_regular_dossiers(self):
        dossier1 = create(Builder('private_dossier').titled(u'Zuz\xfcge'))
        dossier2 = create(Builder('private_dossier').titled(u'Abg\xe4nge'))

        self.assertEquals('dossier-1', dossier1.getId())
        self.assertEquals('dossier-2', dossier2.getId())

    def test_uses_the_same_sequence_counter_as_regular_dossiers(self):
        dossier1 = create(Builder('private_dossier'))
        dossier2 = create(Builder('dossier'))
        dossier3 = create(Builder('private_dossier'))

        sequence_number = getUtility(ISequenceNumber)
        self.assertEquals(1, sequence_number.get_number(dossier1))
        self.assertEquals(2, sequence_number.get_number(dossier2))
        self.assertEquals(3, sequence_number.get_number(dossier3))

    def test_uses_the_same_reference_number_schema_as_regular_dossiers(self):
        dossier1 = create(Builder('private_dossier')
                          .within(self.folder)
                          .having(userid=TEST_USER_ID))
        dossier2 = create(Builder('private_dossier')
                          .within(self.folder)
                          .having(userid=TEST_USER_ID))

        self.assertEquals('Client1 test_user_1_ / 1',
                          IReferenceNumber(dossier1).get_number())
        self.assertEquals('Client1 test_user_1_ / 2',
                          IReferenceNumber(dossier2).get_number())
