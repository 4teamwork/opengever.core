from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestUIActionsGET(IntegrationTestCase):

    @browsing
    def test_ui_actions_without_categories_param(self, browser):
        self.login(self.regular_user, browser)
        url = u'{}/@ui-actions'.format(self.dossier.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual({u'@id': url}, browser.json)

    @browsing
    def test_ui_actions_includes_all_categories(self, browser):
        self.login(self.regular_user, browser)
        url = u'{}/@ui-actions?categories:list=context_actions&categories:list=listing_actions'\
              u'&categories:list=webactions'.format(self.dossier.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual([u'context_actions', u'listing_actions', u'@id', u'webactions'],
                         browser.json.keys())

    @browsing
    def test_ui_actions_includes_context_actions(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@ui-actions?categories:list=context_actions'.format(self.dossier.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            {u'@id': url,
             u'context_actions': [
                {u'id': u'document_with_template'},
                {u'id': u'edit'},
                {u'id': u'export_pdf'},
                {u'id': u'pdf_dossierdetails'},
                {u'id': u'zipexport'},
                {u'id': u'transfer_dossier_responsible'}]}, browser.json)

    @browsing
    def test_ui_actions_includes_listing_actions(self, browser):
        self.login(self.regular_user, browser)
        url = u'{}/@ui-actions?categories:list=listing_actions'\
              u'&listings:list=proposals'.format(self.dossier.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            {u'@id': url,
             u'listing_actions': [{u'id': u'export_proposals'}]}, browser.json)

    @browsing
    def test_listing_actions_with_multiple_listings_returns_intersection(self, browser):
        self.login(self.regular_user, browser)
        task_url = u'{}/@ui-actions?categories:list=listing_actions'\
                   u'&listings:list=tasks'.format(self.dossier.absolute_url())
        browser.open(task_url, method='GET', headers=self.api_headers)
        self.assertEqual([u'close_tasks', u'move_items', u'export_tasks', u'pdf_taskslisting'],
                         [action['id'] for action in browser.json['listing_actions']])
        dossier_url = u'{}/@ui-actions?categories:list=listing_actions'\
                      u'&listings:list=dossiers'.format(self.dossier.absolute_url())
        browser.open(dossier_url, method='GET', headers=self.api_headers)
        self.assertEqual([u'edit_items', u'change_items_state', u'copy_items',
                          u'move_items', u'export_dossiers', u'export_dossiers_with_subdossiers',
                          u'pdf_dossierlisting', u'transfer_dossier_responsible'],
                         [action['id'] for action in browser.json['listing_actions']])
        combined_url = u'{}/@ui-actions?categories:list=listing_actions'\
                       u'&listings:list=tasks&listings:list=dossiers'.format(
                        self.dossier.absolute_url())
        browser.open(combined_url, method='GET', headers=self.api_headers)
        self.assertEqual([u'move_items'],
                         [action['id'] for action in browser.json['listing_actions']])

    @browsing
    def test_listing_actions_without_listings_param_returns_empty_list(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@ui-actions?categories:list=listing_actions'.format(self.dossier.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual([], browser.json['listing_actions'])

    @browsing
    def test_ui_actions_includes_webactions(self, browser):
        self.login(self.webaction_manager, browser)
        create(Builder('webaction')
               .having(
                   title=u'Open in ExternalApp',
                   enabled=True,
            ))
        create(Builder('webaction')
               .having(
                   title=u'Open in InternalApp',
                   enabled=True,
        ))
        create(Builder('webaction')
               .having(
                   title=u'Open in BrokenApp',
                   enabled=False,
            ))

        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='/@ui-actions?categories:list=webactions',
                     method='GET', headers=self.api_headers)

        self.assertEqual(
            [u'Open in ExternalApp', u'Open in InternalApp'],
            [action.get('title') for action in browser.json.get('webactions')])

    @browsing
    def test_webaction_serialization_in_ui_actions_endpoint(self, browser):
        self.login(self.webaction_manager, browser)
        create(Builder('webaction').having(
            target_url='http://localhost/foo?location={path}'))

        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='/@ui-actions?categories:list=webactions',
                     method='GET', headers=self.api_headers)

        self.assertEqual([
            {
                u'action_id': 0,
                u'display': u'actions-menu',
                u'mode': u'self',
                u'icon_data': None,
                u'icon_name': None,
                u'target_url': u'http://localhost/foo?location=%2Fplone%2Fordnungssystem%2F'
                               u'fuhrung%2Fvertrage-und-vereinbarungen%2Fdossier-1&'
                               u'context=http%3A%2F%2Fnohost%2Fplone%2Fordnungssystem%2Ffuhrung'
                               u'%2Fvertrage-und-vereinbarungen%2Fdossier-1&orgunit=fa',
                u'title': u'Open in ExternalApp'
            }],
            browser.json.get('webactions'))
