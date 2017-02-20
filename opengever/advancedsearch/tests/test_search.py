from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import FormFieldNotFound
from opengever.core.testing import activate_filing_number
from opengever.core.testing import inactivate_filing_number
from opengever.testing import FunctionalTestCase
import urllib


class TestSearchForm(FunctionalTestCase):

    @browsing
    def test_filing_number_fields_is_hidden_in_site_without_filing_number_support(self, browser):
        browser.login().open(self.portal, view='advanced_search')

        with self.assertRaises(FormFieldNotFound):
            browser.fill({'Filing number': 'Test'})


class TestSearchFormWithFilingNumberSupport(FunctionalTestCase):

    def setUp(self):
        super(TestSearchFormWithFilingNumberSupport, self).setUp()
        activate_filing_number(self.portal)

    def tearDown(self):
        super(TestSearchFormWithFilingNumberSupport, self).tearDown()
        inactivate_filing_number(self.portal)

    @browsing
    def test_filing_number_field_is_displayed_in_a_filing_number_supported_site(self, browser):
        browser.login().open(view='advanced_search')
        browser.fill({'Filing number': 'Test'})


class TestSearchFormObjectProvidesDescription(FunctionalTestCase):

    @browsing
    def test_contains_special_info_in_a_multi_client_setup(self, browser):
        create(Builder('admin_unit'))

        browser.login().open(self.portal, view='advanced_search')

        self.assertEquals(
            ['Select the contenttype to be searched for.It searches '
             'only items from the current client.'],
            browser.css('#formfield-form-widgets-object_provides span.formHelp').text)

    @browsing
    def test_not_contains_client_info_in_a_single_client_setup(self, browser):
        browser.login().open(self.portal, view='advanced_search')

        self.assertEquals(
            ['Select the contenttype to be searched for.'],
            browser.css('#formfield-form-widgets-object_provides span.formHelp').text)


class TestSearchWithContent(FunctionalTestCase):

    def setUp(self):
        super(TestSearchWithContent, self).setUp()

        self.dossier1 = create(Builder("dossier").titled(u"Dossier1"))
        self.dossier2 = create(Builder("dossier").titled(u"Dossier2"))

    @browsing
    def test_search_dossiers(self, browser):
        browser.login().open(self.dossier1, view='advanced_search')
        browser.fill({
            'Text': "dossier1",
            'Type': ['opengever.dossier.behaviors.dossier.IDossierMarker']})
        browser.css('#form-buttons-button_search').first.click()

        self.assertEquals(['1'], browser.css('#search-results-number').text)
        self.assertEquals(
            'http://nohost/plone/@@search?object_provides=opengever.dossier.behaviors.dossier.IDossierMarker&SearchableText=dossier1',
            browser.url)

    @browsing
    def test_search_documents(self, browser):
        create(Builder("document").within(self.dossier1).titled("Document1"))
        create(Builder("document").within(self.dossier2).titled("Document2"))

        # search documents (we can't find the document because we must
        # change the content-type)
        browser.login().open(self.dossier1, view='advanced_search')
        browser.fill({
            'Text': "document1",
            'Type': ['opengever.dossier.behaviors.dossier.IDossierMarker']})
        browser.css('#form-buttons-button_search').first.click()
        self.assertEquals(['0'], browser.css('#search-results-number').text)

        # search documents with the right content-type
        browser.open(self.dossier1, view='advanced_search')
        browser.fill({
            'Text': "document1",
            'Type': ['opengever.document.behaviors.IBaseDocument']})
        browser.css('#form-buttons-button_search').first.click()

        self.assertEquals(['1'], browser.css('#search-results-number').text)
        self.assertEquals(['Document1'], browser.css('.searchItem dt').text)

    @browsing
    def test_search_tasks(self, browser):
        create(Builder("task").within(self.dossier1).titled("Task1"))
        create(Builder("task").within(self.dossier2).titled("Task2"))

        # search tasks (we can't find the task because we must change
        # the content-type)
        browser.login().open(self.dossier1, view='advanced_search')
        browser.fill({
            'Text': "task1",
            'Type': ['opengever.dossier.behaviors.dossier.IDossierMarker']})
        browser.css('#form-buttons-button_search').first.click()
        self.assertEquals(['0'], browser.css('#search-results-number').text)

        # search tasks with the right content-type
        browser.login().open(self.dossier1, view='advanced_search')
        browser.fill({
            'Text': "task1",
            'Type': ['opengever.task.task.ITask']})
        browser.css('#form-buttons-button_search').first.click()
        self.assertEquals(['1'], browser.css('#search-results-number').text)
        self.assertEquals(['Task1'], browser.css('.searchItem dt').text)


class TestSearchWithoutContent(FunctionalTestCase):

    def setUp(self):
        super(TestSearchWithoutContent, self).setUp()

        activate_filing_number(self.portal)

        self.dossier1 = create(Builder("dossier"))

    def tearDown(self):
        super(TestSearchWithoutContent, self).tearDown()

        inactivate_filing_number(self.portal)

    def assertBrowserUrlContainsSearchParams(self, browser, params):
        url = "http://nohost/plone/@@search?{}".format(urllib.urlencode(params))
        self.assertEqual(browser.url, url)

    @browsing
    def test_date_min_or_max_range_is_queried(self, browser):
        browser.login()
        browser.open(view='advanced_search')
        browser.fill({'form.widgets.object_provides': 'opengever.dossier.behaviors.dossier.IDossierMarker',
                      'form.widgets.start_1': "01.01.2010",
                      'form.widgets.end_2': "01.04.2010"})
        browser.css('#form-buttons-button_search').first.click()

        self.assertBrowserUrlContainsSearchParams(browser, [
            ('object_provides', 'opengever.dossier.behaviors.dossier.IDossierMarker'),
            ('start_usage', 'min'),
            ('start:list', '01/01/10'),
            ('end_usage', 'max'),
            ('end:list', '04/02/10'),
        ])

    @browsing
    def test_validate_searchstring_for_dossiers(self, browser):
        create(Builder('ogds_user')
               .having(firstname='Foo', lastname='Boss',
                       userid='foo@example.com'))

        browser.login().open(view='advanced_search')
        browser.fill({'form.widgets.searchableText': "dossier1",
                      'form.widgets.object_provides': ['opengever.dossier.behaviors.dossier.IDossierMarker'],
                      'form.widgets.start_1': "01.01.2010",
                      'form.widgets.start_2': "01.02.2010",
                      'form.widgets.end_1': "01.03.2010",
                      'form.widgets.end_2': "01.04.2010",
                      'form.widgets.reference': "OG 14.2",
                      'form.widgets.sequence_number': "5",
                      'form.widgets.searchable_filing_no': "14",
                      'Responsible': "foo@example.com",
                      'form.widgets.dossier_review_state:list': 'dossier-state-active'})
        browser.css('#form-buttons-button_search').first.click()

        self.assertBrowserUrlContainsSearchParams(browser, [
            ('object_provides', 'opengever.dossier.behaviors.dossier.IDossierMarker'),
            ('SearchableText', 'dossier1'),
            ('start_usage', 'minmax'),
            ('start:list', '01/01/10'),
            ('start:list', '02/02/10'),
            ('end_usage', 'minmax'),
            ('end:list', '03/01/10'),
            ('end:list', '04/02/10'),
            ('reference', 'OG 14.2'),
            ('sequence_number:int', '5'),
            ('searchable_filing_no', '14'),
            ('responsible', 'foo@example.com'),
            ('review_state:list', 'dossier-state-active'),
        ])

    @browsing
    def test_validate_searchstring_for_documents(self, browser):
        browser.login().open(view='advanced_search')
        browser.fill({'form.widgets.searchableText': "document1",
                      'form.widgets.object_provides': 'opengever.document.behaviors.IBaseDocument',
                      'form.widgets.receipt_date_1': "01.01.2010",
                      'form.widgets.receipt_date_2': "01.02.2010",
                      'form.widgets.delivery_date_1': "01.03.2010",
                      'form.widgets.delivery_date_2': "01.04.2010",
                      'form.widgets.document_author': "Eduard",
                      'form.widgets.sequence_number': "5",
                      'form.widgets.trashed:list': True})
        browser.css('#form-buttons-button_search').first.click()

        self.assertBrowserUrlContainsSearchParams(browser, [
            ('object_provides', 'opengever.document.behaviors.IBaseDocument'),
            ('SearchableText', 'document1'),
            ('receipt_date_usage', 'minmax'),
            ('receipt_date:list', '01/01/10'),
            ('receipt_date:list', '02/02/10'),
            ('delivery_date_usage', 'minmax'),
            ('delivery_date:list', '03/01/10'),
            ('delivery_date:list', '04/02/10'),
            ('document_author', 'Eduard'),
            ('trashed:list:boolean', 'True'),
            ('trashed:list:boolean', 'False'),
        ])

    @browsing
    def test_validate_searchstring_for_tasks(self, browser):
        browser.login().open(view='advanced_search')
        browser.fill({'form.widgets.searchableText': "task1",
                      'form.widgets.object_provides': 'opengever.task.task.ITask',
                      'form.widgets.deadline_1': "01.01.2010",
                      'form.widgets.deadline_2': "01.02.2010",
                      'form.widgets.task_type:list': 'information',
                      'form.widgets.dossier_review_state:list': 'dossier-state-active'})
        browser.css('#form-buttons-button_search').first.click()

        self.assertBrowserUrlContainsSearchParams(browser, [
            ('object_provides', 'opengever.task.task.ITask'),
            ('SearchableText', 'task1'),
            ('deadline_usage', 'minmax'),
            ('deadline:list', '01/01/10'),
            ('deadline:list', '02/02/10'),
            ('task_type', 'information'),
        ])

    @browsing
    def test_disable_unload_protection(self, browser):
        browser.login().open(view='advanced_search')
        self.assertNotIn('enableUnloadProtection', browser.contents)
