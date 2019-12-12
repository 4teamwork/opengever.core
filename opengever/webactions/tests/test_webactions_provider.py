from ftw.builder import Builder
from ftw.builder import create
from opengever.base.public_permissions import PUBLIC_PERMISSIONS_MAPPING
from opengever.testing import IntegrationTestCase
from opengever.webactions.interfaces import IWebActionsProvider
from opengever.webactions.schema import ACTION_PERMISSIONS
from opengever.webactions.storage import get_storage
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter


class TestWebActionBase(IntegrationTestCase):

    def clear_request_cache(self):
        """ This is needed as user permissions, group memberships
        and action availability on scope get cached on the request
        and in the test we can change any of these or the context itself
        in the same request...
        """
        IAnnotations(self.request).pop('plone.memoize')


class TestWebActionProvider(TestWebActionBase):

    def setUp(self):
        super(TestWebActionProvider, self).setUp()

        create(Builder('webaction')
               .titled(u'Action 1')
               .having(order=5))

        create(Builder('webaction')
               .titled(u'Action 2')
               .having(order=10))

        create(Builder('webaction')
               .titled(u'Action 3')
               .having(order=20))

        self.action1_data = {'target_url': 'http://example.org/endpoint',
                             'title': u'Action 1',
                             'icon_name': None,
                             'mode': 'self',
                             'icon_data': None,
                             'action_id': 0}

        self.action2_data = {'target_url': 'http://example.org/endpoint',
                             'title': u'Action 2',
                             'icon_name': None,
                             'mode': 'self',
                             'icon_data': None,
                             'action_id': 1}

        self.action3_data = {'target_url': 'http://example.org/endpoint',
                             'title': u'Action 3',
                             'icon_name': None,
                             'mode': 'self',
                             'icon_data': None,
                             'action_id': 2}

    def test_data_returned_by_webaction_provider(self):
        """ This test also asserts the initial state and returned
        data, serving as basis for the other tests in this class.
        """
        self.login(self.regular_user)
        provider = getMultiAdapter((self.dossier, self.request), IWebActionsProvider)
        webactions = provider.get_webactions()

        expected_data = {'actions-menu': [self.action1_data,
                                          self.action2_data,
                                          self.action3_data]}

        self.assertDictEqual(expected_data, webactions)

    def test_webaction_provider_returns_dict_with_correct_display_as_key(self):
        self.login(self.regular_user)
        provider = getMultiAdapter((self.dossier, self.request), IWebActionsProvider)

        storage = get_storage()
        storage.update(1, {"display": "action-buttons"})
        storage.update(2, {"display": "user-menu"})

        expected_data = {'actions-menu': [self.action1_data],
                         'action-buttons': [self.action2_data],
                         'user-menu': [self.action3_data]}

        webactions = provider.get_webactions()

        self.assertDictEqual(expected_data, webactions)

    def test_webaction_provider_only_returns_enabled_actions(self):
        self.login(self.regular_user)
        provider = getMultiAdapter((self.dossier, self.request), IWebActionsProvider)

        storage = get_storage()
        storage.update(1, {"enabled": False})

        expected_data = {'actions-menu': [self.action1_data, self.action3_data]}
        self.assertDictEqual(expected_data, provider.get_webactions())

    def test_webaction_provider_only_returns_actions_with_global_scope(self):
        self.login(self.regular_user)
        provider = getMultiAdapter((self.dossier, self.request), IWebActionsProvider)
        storage = get_storage()
        # XXX We can't use storage.update here, as only the global scope is
        # implemented and allowed for now
        storage._actions[0]["scope"] = "context"
        storage._actions[2]["scope"] = "recursive"

        expected_data = {'actions-menu': [self.action2_data]}
        self.assertDictEqual(expected_data, provider.get_webactions())

    def test_webaction_provider_respects_portal_type(self):
        self.login(self.regular_user)
        storage = get_storage()
        storage.update(0, {"types": ['opengever.document.document']})
        storage.update(1, {"types": ['opengever.document.document',
                                     'opengever.dossier.businesscasedossier']})

        provider = getMultiAdapter((self.dossier, self.request),
                                   IWebActionsProvider)

        expected_data = {'actions-menu': [self.action2_data, self.action3_data]}
        self.assertItemsEqual(expected_data, provider.get_webactions())

        self.clear_request_cache()
        provider = getMultiAdapter((self.document, self.request),
                                   IWebActionsProvider)

        expected_data = {'actions-menu': [self.action1_data,
                                          self.action2_data,
                                          self.action3_data]}
        self.assertDictEqual(expected_data, provider.get_webactions())

        self.clear_request_cache()
        provider = getMultiAdapter((self.leaf_repofolder, self.request),
                                   IWebActionsProvider)

        expected_data = {'actions-menu': [self.action3_data]}
        self.assertDictEqual(expected_data, provider.get_webactions())

    def test_all_action_permissions_are_in_public_permissions_mapping(self):
        for permission in ACTION_PERMISSIONS:
            self.assertIn(
                permission, PUBLIC_PERMISSIONS_MAPPING.keys(),
                "All action permissions need to be mapped to real permissions")

    def test_webaction_provider_respects_permission(self):
        self.login(self.regular_user)
        storage = get_storage()
        storage.update(0, {"permissions": ['trash']})
        storage.update(1, {"permissions": ['trash', 'edit']})
        storage.update(2, {"permissions": ['edit']})

        self.dossier.manage_permission("opengever.trash: Trash content", ["Manager"])
        self.dossier.manage_permission('Modify portal content', ["Administrator"])

        provider = getMultiAdapter((self.dossier, self.request),
                                   IWebActionsProvider)

        self.assertDictEqual({}, provider.get_webactions())

        self.login(self.manager)
        expected_data = {'actions-menu': [self.action1_data, self.action2_data]}
        self.assertDictEqual(expected_data, provider.get_webactions())

        self.login(self.administrator)
        expected_data = {'actions-menu': [self.action2_data, self.action3_data]}
        self.assertDictEqual(expected_data, provider.get_webactions())

    def test_webaction_provider_respects_groups(self):
        self.login(self.regular_user)
        storage = get_storage()
        storage.update(0, {"groups": [u'fa_inbox_users']})
        storage.update(1, {"groups": [u'fa_inbox_users', u'committee_rpk_group']})
        storage.update(2, {"groups": [u'committee_rpk_group']})

        provider = getMultiAdapter((self.dossier, self.request),
                                   IWebActionsProvider)

        self.assertDictEqual({}, provider.get_webactions())

        self.login(self.secretariat_user)
        expected_data = {'actions-menu': [self.action1_data, self.action2_data]}
        self.assertDictEqual(expected_data, provider.get_webactions())

        self.login(self.committee_responsible)
        expected_data = {'actions-menu': [self.action2_data, self.action3_data]}
        self.assertDictEqual(expected_data, provider.get_webactions())

    def test_webaction_provider_sorts_actions(self):
        self.login(self.regular_user)
        provider = getMultiAdapter((self.dossier, self.request), IWebActionsProvider)

        expected_data = [self.action1_data, self.action2_data, self.action3_data]
        self.assertEqual(expected_data, provider.get_webactions()['actions-menu'])

        self.clear_request_cache()
        storage = get_storage()
        storage.update(0, {"order": 50})
        storage.update(2, {"order": 1})

        expected_data = [self.action3_data, self.action2_data, self.action1_data]
        self.assertEqual(expected_data, provider.get_webactions()['actions-menu'])
