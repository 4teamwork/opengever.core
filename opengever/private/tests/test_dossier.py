from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.interfaces import ISequenceNumber
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from opengever.trash.trash import ITrashable
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.protect import createToken
from zope.component import getUtility


class TestPrivateDossier(IntegrationTestCase):

    features = ('private', )

    @browsing
    def test_is_addable_to_a_private_folder(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_folder)
        factoriesmenu.add('Private Dossier')
        browser.fill({'Title': u'My Personal Stuff'})
        browser.click_on('Save')

        self.assertEquals([u'My Personal Stuff'],
                          browser.css('h1.documentFirstHeading').text)

    @browsing
    def test_responsible_is_current_user_by_default(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_folder)

        factoriesmenu.add('Private Dossier')
        browser.fill({'Title': u'My Personal Stuff'})
        browser.click_on('Save')

        self.assertEquals(
            self.regular_user.getId(),
            IDossier(browser.context).responsible)

    def test_use_same_id_schema_as_regular_dossiers(self):
        self.login(self.regular_user)
        self.assertEquals(
            ['dossier-14', 'dossier-15'],
            [dos.getId() for dos in self.private_folder.listFolderContents()])

    def test_uses_the_same_sequence_counter_as_regular_dossiers(self):
        self.login(self.regular_user)

        sequence_number = getUtility(ISequenceNumber)
        self.assertEquals(
            [14, 15],
            [sequence_number.get_number(dos) for dos
             in self.private_folder.listFolderContents()])

    def test_allow_one_level_of_subdossiers(self):
        self.login(self.regular_user)

        subdossier = create(Builder('private_dossier')
                            .within(self.private_dossier)
                            .having(responsible=TEST_USER_ID))

        self.assertItemsEqual(
            ['opengever.document.document',
             'ftw.mail.mail',
             'opengever.private.dossier'],
            [fti.id for fti in self.private_dossier.allowedContentTypes()])

        self.assertItemsEqual(
            ['opengever.document.document', 'ftw.mail.mail'],
            [fti.id for fti in subdossier.allowedContentTypes()])

    def test_does_not_support_participations(self):
        self.login(self.regular_user)
        self.assertFalse(self.private_dossier.has_participation_support())

    def test_does_not_support_tasks(self):
        self.login(self.regular_user)
        self.assertFalse(self.private_dossier.has_task_support())


class TestPrivateDossierTabbedView(IntegrationTestCase):

    features = ('private', )

    @browsing
    def test_task_proposal_participations_and_info_tab_are_hidden(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_dossier)

        self.assertEquals(
            ['Overview', 'Subdossiers', 'Documents', 'Trash', 'Journal'],
            browser.css('.formTab').text)

    @browsing
    def test_action_menu_is_displayed_correctly(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_dossier)

        self.assertEqual(
            ['Delete', 'Export as Zip', 'Properties',
             'dossier-transition-resolve'],
            editbar.menu_options("Actions"))

    @browsing
    def test_participation_and_task_box_are_hidden_on_overview(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_dossier, view='tabbedview_view-overview')

        self.assertEquals(
            ['Dossier structure', 'Comments', 'Linked Dossiers',
             'Newest documents', 'Description', 'Keywords'],
            browser.css('.box h2').text)

    def test_columns_are_hidden_in_documents_tab(self):
        """Some columns do not make a lot of sense in a private dossier.
        We hide them in the default configuration.
        """
        self.login(self.regular_user)

        view = self.private_dossier.unrestrictedTraverse(
            'tabbedview_view-documents')
        columns_by_name = {col['column']: col for col in view.columns}

        self.assertTrue(columns_by_name['public_trial'].get('hidden', None))
        self.assertTrue(columns_by_name['receipt_date'].get('hidden', None))
        self.assertTrue(columns_by_name['delivery_date'].get('hidden', None))


class TestPrivateDossierWorkflow(IntegrationTestCase):

    features = ('private', )

    @browsing
    def test_tasks_and_propsoals_are_not_addable(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_dossier)

        self.assertEquals(
            ['Document',
             'document_with_template',
             'Subdossier'],
            factoriesmenu.addable_types())

    @browsing
    def test_adding_subdossiers_is_allowed(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_dossier)

        factoriesmenu.add('Subdossier')
        browser.fill({'Title': u'Sub 1'})
        browser.click_on('Save')

        self.assertEquals(['Item created'], info_messages())

    @browsing
    def test_trashing_documents_in_private_folder_is_possible(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_dossier)

        data = {'paths:list': ['/'.join(self.private_document.getPhysicalPath())],
                '_authenticator': createToken()}

        browser.open(self.private_dossier, view="trashed", data=data)
        self.assertEquals([u'the object Testdokum\xe4nt trashed'],
                          info_messages())

    @browsing
    def test_private_dossier_can_be_resolved(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_dossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertEquals(['The dossier has been succesfully resolved.'],
                          info_messages())
        self.assertEqual('dossier-state-resolved',
                         api.content.get_state(self.private_dossier))

    @browsing
    def test_accessing_dossier_via_rest_api(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(
            self.private_dossier.absolute_url(), method='GET',
            headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'Mein Dossier 1', browser.json['title'])
        self.assertEqual(
            {u'@id': u'http://nohost/plone/private/kathi-barfuss',
             u'@type': u'opengever.private.folder',
             u'description': u'',
             u'is_subdossier': None,
             u'review_state': u'folder-state-active',
             u'title': u'B\xe4rfuss K\xe4thi (kathi.barfuss)'},
            browser.json['parent'])


class TestPrivateDossierWorkflowSolr(SolrIntegrationTestCase):

    features = ('private', )

    @browsing
    def test_remove_action_not_available_in_private_folder(self, browser):
        self.login(self.manager, browser=browser)

        ITrashable(self.document).trash()
        self.commit_solr()

        browser.open(self.dossier, view="tabbed_view/listing?view_name=trash")
        self.assertItemsEqual([u'More actions \u25bc', 'untrashed', 'remove'],
                              browser.css('#tabbedview-menu a').text)

        ITrashable(self.private_document).trash()
        self.commit_solr()

        browser.open(self.private_dossier, view="tabbed_view/listing?view_name=trash")
        self.assertItemsEqual([u'More actions \u25bc', 'untrashed'],
                              browser.css('#tabbedview-menu a').text)
