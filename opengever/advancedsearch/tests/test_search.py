from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import FormFieldNotFound
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.testing import IntegrationTestCase
import urllib
import urlparse


class TestSearchForm(IntegrationTestCase):

    @browsing
    def test_filing_number_fields_is_hidden_in_site_without_filing_number_support(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='advanced_search')

        with self.assertRaises(FormFieldNotFound):
            browser.fill({'Filing number': 'Test'})


class TestSearchFormWithFilingNumberSupport(IntegrationTestCase):

    features = ('filing_number', )

    @browsing
    def test_filing_number_field_is_displayed_in_a_filing_number_supported_site(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='advanced_search')

        browser.fill({'Filing number': u'FD-112'})


class TestSearchFormObjectProvidesDescription(IntegrationTestCase):

    @browsing
    def test_contains_special_info_in_a_multi_client_setup(self, browser):
        create(Builder('admin_unit').id("additional"))

        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='advanced_search')

        self.assertEquals(
            ['Select the contenttype to be searched for.It searches '
             'only items from the current client.'],
            browser.css('#formfield-form-widgets-object_provides span.formHelp').text)

    @browsing
    def test_not_contains_client_info_in_a_single_client_setup(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='advanced_search')

        self.assertEquals(
            ['Select the contenttype to be searched for.'],
            browser.css('#formfield-form-widgets-object_provides span.formHelp').text)


class TestSearchWithContent(IntegrationTestCase):

    @browsing
    def test_search_dossiers(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal, view='advanced_search')
        browser.fill({
            'Text': "kantonalen Finanzverwaltung",
            'Type': ['opengever.dossier.behaviors.dossier.IDossierMarker']})
        browser.css('#form-buttons-button_search').first.click()

        self.assertEquals(['1'], browser.css('#search-results-number').text)
        self.assertEquals(
            'object_provides=opengever.dossier.behaviors.dossier.IDossierMarker'
            '&SearchableText=kantonalen+Finanzverwaltung',
            urlparse.urlparse(browser.url).query)
        self.assertEquals(
            [u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'],
            browser.css('.searchResults .searchItem dt').text)

    @browsing
    def test_search_documents(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal, view='advanced_search')
        browser.fill({
            'Text': u'Vertr\xe4gsentwurf',
            'Type': ['opengever.document.behaviors.IBaseDocument']})
        browser.css('#form-buttons-button_search').first.click()

        self.assertEquals(['3'], browser.css('#search-results-number').text)
        self.assertEquals(
            [self.document.title, self.taskdocument.title,
             self.proposaldocument.title],
            browser.css('.searchResults .searchItem dt').text)

    @browsing
    def test_search_tasks(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='advanced_search')
        browser.fill({
            'Text': "Rechtliche Grundlagen",
            'Type': ['opengever.task.task.ITask']})
        browser.css('#form-buttons-button_search').first.click()

        self.assertEquals(['1'], browser.css('#search-results-number').text)
        self.assertEquals([self.subtask.title],
                          browser.css('.searchResults .searchItem dt').text)

    @browsing
    def test_date_min_queries(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='advanced_search')

        browser.fill({
            'Text': "kantonalen Finanzverwaltung",
            'form.widgets.object_provides': IDossierMarker.__identifier__,
            'form.widgets.start_1': "10.10.2015"})
        browser.css('#form-buttons-button_search').first.click()

        self.assertEquals([self.dossier.title],
                          browser.css('.searchResults .searchItem dt').text)

        browser.open(self.portal, view='advanced_search')
        browser.fill({
            'Text': "kantonalen Finanzverwaltung",
            'form.widgets.object_provides': IDossierMarker.__identifier__,
            'form.widgets.start_1': "10.01.2017"})
        browser.css('#form-buttons-button_search').first.click()
        self.assertEquals([],
                          browser.css('.searchResults .searchItem dt').text)

    @browsing
    def test_date_max_queries(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='advanced_search')

        browser.fill({
            'Text': u'Abgeschlossene Vertr\xe4ge',
            'form.widgets.object_provides': IDossierMarker.__identifier__,
            'form.widgets.end_2': "10.10.2002"})
        browser.css('#form-buttons-button_search').first.click()

        self.assertEquals([self.expired_dossier.title],
                          browser.css('.searchResults .searchItem dt').text)

        browser.open(self.portal, view='advanced_search')
        browser.fill({
            'Text': u'Abgeschlossene Vertr\xe4ge',
            'form.widgets.object_provides': IDossierMarker.__identifier__,
            'form.widgets.end_2': "10.10.1998"})
        browser.css('#form-buttons-button_search').first.click()
        self.assertEquals([],
                          browser.css('.searchResults .searchItem dt').text)

    @browsing
    def test_can_select_dossier_responsible_from_inactive_ou_in_widget(self, browser):
        self.create_inactive_user()
        self.login(self.regular_user, browser=browser)

        # We manually do a request on the widget here because
        # ftw.keywordwidget.tests.widget.AsyncKeywordWidget
        # doesn't support .query() yet
        widget_url = '/'.join((
            self.portal.absolute_url(),
            'advanced_search',
            '++widget++form.widgets.responsible'))
        browser.open(widget_url + '/search?q=without')

        self.assertIn(
            {'id': 'user.without.orgunit',
             'text': 'Orgunit Without (user.without.orgunit)',
             '_resultId': 'user.without.orgunit'},
            browser.json['results'])

    @browsing
    def test_can_select_task_issuer_from_inactive_ou_in_widget(self, browser):
        self.create_inactive_user()
        self.login(self.regular_user, browser=browser)

        # We manually do a request on the widget here because
        # ftw.keywordwidget.tests.widget.AsyncKeywordWidget
        # doesn't support .query() yet
        widget_url = '/'.join((
            self.portal.absolute_url(),
            'advanced_search',
            '++widget++form.widgets.issuer'))
        browser.open(widget_url + '/search?q=without')

        self.assertIn(
            {'id': 'user.without.orgunit',
             'text': 'Orgunit Without (user.without.orgunit)',
             '_resultId': 'user.without.orgunit'},
            browser.json['results'])

    @browsing
    def test_can_select_doc_checked_out_from_inactive_ou_in_widget(self, browser):
        self.create_inactive_user()
        self.login(self.regular_user, browser=browser)

        # We manually do a request on the widget here because
        # ftw.keywordwidget.tests.widget.AsyncKeywordWidget
        # doesn't support .query() yet
        widget_url = '/'.join((
            self.portal.absolute_url(),
            'advanced_search',
            '++widget++form.widgets.checked_out'))
        browser.open(widget_url + '/search?q=without')

        self.assertIn(
            {'id': 'user.without.orgunit',
             'text': 'Orgunit Without (user.without.orgunit)',
             '_resultId': 'user.without.orgunit'},
            browser.json['results'])

    @browsing
    def test_disable_unload_protection(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='advanced_search')

        self.assertNotIn('enableUnloadProtection', browser.contents)


class TestQueryStrings(IntegrationTestCase):

    features = ('filing_number', )

    def assertBrowserUrlContainsSearchParams(self, browser, params):
        url = "http://nohost/plone/@@search?{}".format(urllib.urlencode(params))
        self.assertEqual(browser.url, url)

    @browsing
    def test_validate_searchstring_for_dossiers(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(view='advanced_search')

        browser.fill({'form.widgets.searchableText': "dossier1",
                      'form.widgets.object_provides': ['opengever.dossier.behaviors.dossier.IDossierMarker'],
                      'form.widgets.start_1': "01.01.2010",
                      'form.widgets.start_2': "01.02.2010",
                      'form.widgets.end_1': "01.03.2010",
                      'form.widgets.end_2': "01.04.2010",
                      'form.widgets.reference': "OG 14.2",
                      'form.widgets.sequence_number': "5",
                      'form.widgets.searchable_filing_no': "14",
                      'form.widgets.dossier_review_state:list': 'dossier-state-active'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.regular_user.id)
        browser.css('#form-buttons-button_search').first.click()

        self.assertBrowserUrlContainsSearchParams(browser, [
            ('object_provides', 'opengever.dossier.behaviors.dossier.IDossierMarker'),
            ('SearchableText', 'dossier1'),
            ('start.range:record', 'minmax'),
            ('start.query:record:list:date', '2010-01-01'),
            ('start.query:record:list:date', '2010-02-02'),
            ('end.range:record', 'minmax'),
            ('end.query:record:list:date', '2010-03-01'),
            ('end.query:record:list:date', '2010-04-02'),
            ('reference', 'OG 14.2'),
            ('sequence_number:int', '5'),
            ('searchable_filing_no', '14'),
            ('responsible', self.regular_user.id),
            ('review_state:list', 'dossier-state-active'),
        ])

    @browsing
    def test_validate_searchstring_for_documents(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(view='advanced_search')

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
            ('receipt_date.range:record', 'minmax'),
            ('receipt_date.query:record:list:date', '2010-01-01'),
            ('receipt_date.query:record:list:date', '2010-02-02'),
            ('delivery_date.range:record', 'minmax'),
            ('delivery_date.query:record:list:date', '2010-03-01'),
            ('delivery_date.query:record:list:date', '2010-04-02'),
            ('document_author', 'Eduard'),
            ('trashed:list:boolean', 'True'),
            ('trashed:list:boolean', 'False'),
        ])

    @browsing
    def test_validate_searchstring_for_tasks(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(view='advanced_search')

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
            ('deadline.range:record', 'minmax'),
            ('deadline.query:record:list:date', '2010-01-01'),
            ('deadline.query:record:list:date', '2010-02-02'),
            ('task_type', 'information'),
        ])
