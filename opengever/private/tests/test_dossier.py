from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.core.testing import OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER
from opengever.dossier.behaviors.dossier import IDossier
from opengever.private.tests import create_members_folder
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.protect import createToken
from zope.component import getUtility


class TestPrivateDossier(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER

    def setUp(self):
        super(TestPrivateDossier, self).setUp()
        self.root = create(Builder('private_root'))
        self.folder = create_members_folder(self.root)

    @browsing
    def test_is_addable_to_a_private_folder(self, browser):
        browser.login().open(self.folder)
        factoriesmenu.add('Private Dossier')
        browser.fill({'Title': u'My Personal Stuff',
                      'Responsible': TEST_USER_ID})
        browser.click_on('Save')

        self.assertEquals([u'My Personal Stuff'],
                          browser.css('h1.documentFirstHeading').text)

    @browsing
    def test_responsible_is_current_user_by_default(self, browser):
        browser.login().open(self.folder)
        factoriesmenu.add('Private Dossier')
        browser.fill({'Title': u'My Personal Stuff'})
        browser.click_on('Save')

        self.assertEquals(TEST_USER_ID,
                          IDossier(self.folder.get('dossier-1')).responsible)

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

    def test_allow_one_level_of_subdossiers(self):
        dossier = create(Builder('private_dossier')
                         .within(self.folder)
                         .having(responsible=TEST_USER_ID))
        subdossier = create(Builder('private_dossier')
                            .within(dossier)
                            .having(responsible=TEST_USER_ID))

        self.assertItemsEqual(
            ['opengever.document.document',
             'ftw.mail.mail',
             'opengever.private.dossier'],
            [fti.id for fti in dossier.allowedContentTypes()])

        self.assertItemsEqual(
            ['opengever.document.document', 'ftw.mail.mail'],
            [fti.id for fti in subdossier.allowedContentTypes()])

    def test_does_not_support_participations(self):
        dossier = create(Builder('private_dossier')
                         .within(self.folder)
                         .having(responsible=TEST_USER_ID))
        self.assertFalse(dossier.has_participation_support())

    def test_does_not_support_tasks(self):
        dossier = create(Builder('private_dossier')
                         .within(self.folder)
                         .having(responsible=TEST_USER_ID))
        self.assertFalse(dossier.has_task_support())


class TestPrivateDossierTabbedView(FunctionalTestCase):

    def setUp(self):
        super(TestPrivateDossierTabbedView, self).setUp()
        self.root = create(Builder('private_root'))
        self.folder = create(Builder('private_folder')
                             .having(userid=TEST_USER_ID)
                             .within(self.root))

    @browsing
    def test_task_proposal_participations_and_info_tab_are_hidden(self, browser):
        dossier = create(Builder('private_dossier').within(self.folder))
        browser.login().open(dossier)

        self.assertEquals(
            ['Overview', 'Subdossiers', 'Documents', 'Trash', 'Journal'],
            browser.css('.formTab').text)

    @browsing
    def test_action_menu_is_displayed_correctly(self, browser):
        dossier = create(Builder('private_dossier').within(self.folder))
        browser.login().open(dossier)

        self.assertEqual(
            ['Delete', 'Export as Zip', 'Properties',
             'dossier-transition-resolve'],
            browser.css('#plone-contentmenu-actions '
                        '.actionMenuContent li').text)

    @browsing
    def test_participation_and_task_box_are_hidden_on_overview(self, browser):
        dossier = create(Builder('private_dossier').within(self.folder))
        browser.login().open(dossier, view='tabbedview_view-overview')

        self.assertEquals(
            ['Dossier structure', 'Comments', 'Linked Dossiers',
             'Newest documents', 'Description', 'Keywords'],
            browser.css('.box h2').text)

    def test_columns_are_hidden_in_documents_tab(self):
        """Some columns do not make a lot of sense in a private dossier.
        We hide them in the default configuration.
        """

        dossier = create(Builder('private_dossier').within(self.folder))
        view = dossier.unrestrictedTraverse('tabbedview_view-documents')
        columns_by_name = {col['column']: col for col in view.columns}
        self.assertTrue(columns_by_name['public_trial'].get('hidden', None))
        self.assertTrue(columns_by_name['receipt_date'].get('hidden', None))
        self.assertTrue(columns_by_name['delivery_date'].get('hidden', None))


class TestPrivateDossierWorkflow(FunctionalTestCase):

    def setUp(self):
        super(TestPrivateDossierWorkflow, self).setUp()
        self.root = create(Builder('private_root'))
        self.folder = create(Builder('private_folder')
                             .having(userid=TEST_USER_ID)
                             .within(self.root))
        self.dossier = create(Builder('private_dossier').within(self.folder))

    @browsing
    def test_tasks_and_propsoals_are_not_addable(self, browser):
        browser.login().open(self.dossier)

        self.assertEquals(
            ['Document',
             'document_with_template',
             'Subdossier'],
            factoriesmenu.addable_types())

    @browsing
    def test_adding_subdossiers_is_allowed(self, browser):
        browser.login().open(self.dossier)
        factoriesmenu.add('Subdossier')
        browser.fill({'Title': u'Sub 1',
                      'Responsible': TEST_USER_ID})
        browser.click_on('Save')

        self.assertEquals(['Item created'], info_messages())

    @browsing
    def test_trashing_documents_in_private_folder_is_possible(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .titled(u'My private document'))

        data = {'paths:list': ['/'.join(document.getPhysicalPath())],
                '_authenticator': createToken()}

        self.grant('Member', 'Reader')

        browser.login().open(self.dossier, view="trashed", data=data)

        self.assertEquals([u'the object My private document trashed'],
                          info_messages())

    @browsing
    def test_private_dossier_can_be_resolved(self, browser):
        browser.login().open(self.dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')
        self.assertEquals(['The dossier has been succesfully resolved.'],
                          info_messages())

        self.assertEqual('dossier-state-resolved',
                         api.content.get_state(self.dossier))
