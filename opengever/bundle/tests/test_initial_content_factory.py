from collections import OrderedDict
from opengever.base.model import create_session
from opengever.bundle.initial_content import InitialContentFactory
from opengever.ogds.models.service import ogds_service
from opengever.testing import IntegrationTestCase


class TestInitialContentFactory(IntegrationTestCase):

    def setUp(self):
        super(TestInitialContentFactory, self).setUp()

    def test_doesnt_produce_content_if_items_already_in_bundle(self):
        bundle_content_counts = {
            'inboxcontainers.json': 1,
            'inboxes.json': 1,
            'privateroots.json': 1,
            'templatefolders.json': 1,
        }
        initial_content = InitialContentFactory().generate(bundle_content_counts)
        self.assertEqual({}, initial_content)

    def test_produces_inboxes_in_container_for_setup_with_multiple_org_units(self):
        bundle_content_counts = {
            'inboxcontainers.json': 0,
            'inboxes.json': 0,
            'privateroots.json': 1,
            'templatefolders.json': 1,
        }

        STATIC_INBOX_CONTAINER_GUID = 'inbox-container'

        initial_content = InitialContentFactory().generate(bundle_content_counts)
        expected = OrderedDict([(
            'inboxcontainers.json', [
                {
                    'guid': STATIC_INBOX_CONTAINER_GUID,
                    '_id': 'eingangskorb',
                    'title_de': 'Eingangskorb',
                    'title_fr': 'Bo\xc3\xaete de r\xc3\xa9ception',
                    'title_en': 'Inbox',
                    'review_state': 'inbox-state-default',
                    '_permissions': {
                        'read': [
                            'fa_inbox_users',
                            'rk_inbox_users',
                        ]},
                },
            ]), (
            'inboxes.json', [
                {
                    'guid': 'inbox-fa',
                    'parent_guid': STATIC_INBOX_CONTAINER_GUID,
                    '_id': 'fa',
                    'title_de': u'Eingangskorb Finanz\xe4mt',
                    'title_fr': u'Bo\xeete de r\xe9ception Finanz\xe4mt',
                    'title_en': u'Inbox Finanz\xe4mt',
                    'review_state': 'inbox-state-default',

                    'responsible_org_unit': u'fa',
                    '_permissions': {
                        'read': ['fa_inbox_users'],
                        'edit': ['fa_inbox_users'],
                        'add': ['fa_inbox_users'],
                        'block_inheritance': True},
                },
                {
                    'guid': 'inbox-rk',
                    'parent_guid': STATIC_INBOX_CONTAINER_GUID,
                    '_id': 'rk',
                    'title_de': u'Eingangskorb Ratskanzl\xc3\xa4i',
                    'title_fr': u'Bo\xeete de r\xe9ception Ratskanzl\xc3\xa4i',
                    'title_en': u'Inbox Ratskanzl\xc3\xa4i',
                    'review_state': 'inbox-state-default',

                    'responsible_org_unit': u'rk',
                    '_permissions': {
                        'read': ['rk_inbox_users'],
                        'edit': ['rk_inbox_users'],
                        'add': ['rk_inbox_users'],
                        'block_inheritance': True},
                },
            ]
        )])
        self.assertEqual(expected, initial_content)

    def test_produces_single_inbox_at_top_level_for_setup_with_single_org_unit(self):
        bundle_content_counts = {
            'inboxcontainers.json': 0,
            'inboxes.json': 0,
            'privateroots.json': 1,
            'templatefolders.json': 1,
        }

        last_ou = ogds_service().all_org_units()[-1]
        create_session().delete(last_ou)
        self.assertEqual(1, len(ogds_service().all_org_units()))

        initial_content = InitialContentFactory().generate(bundle_content_counts)
        expected = OrderedDict([(
            'inboxcontainers.json', []), (
            'inboxes.json', [
                {
                    'guid': 'inbox-fa',
                    '_id': 'eingangskorb',
                    'title_de': 'Eingangskorb',
                    'title_fr': 'Bo\xc3\xaete de r\xc3\xa9ception',
                    'title_en': 'Inbox',
                    'review_state': 'inbox-state-default',

                    'responsible_org_unit': 'fa',
                    '_permissions': {
                        'read': ['fa_inbox_users'],
                        'edit': ['fa_inbox_users'],
                        'add': ['fa_inbox_users']},
                }],
        )])
        self.assertEqual(expected, initial_content)

    def test_produces_private_root(self):
        bundle_content_counts = {
            'inboxcontainers.json': 1,
            'inboxes.json': 1,
            'privateroots.json': 0,
            'templatefolders.json': 1,
        }
        initial_content = InitialContentFactory().generate(bundle_content_counts)
        expected = OrderedDict([(
            'privateroots.json', [{
                'guid': 'private-root',
                '_id': 'private',
                'title_de': 'Meine Ablage',
                'title_fr': 'Dossier personnel',
                'title_en': 'My repository',
                'review_state': 'repositoryroot-state-active',  # [sic]
            }]
        )])
        self.assertEqual(expected, initial_content)

    def test_produces_template_folder(self):
        bundle_content_counts = {
            'inboxcontainers.json': 1,
            'inboxes.json': 1,
            'privateroots.json': 1,
            'templatefolders.json': 0,
        }
        initial_content = InitialContentFactory().generate(bundle_content_counts)
        expected = OrderedDict([(
            'templatefolders.json', [{
                'guid': 'template-folder',
                '_id': 'vorlagen',
                'title_de': 'Vorlagen',
                'title_fr': 'Mod\xc3\xa8les',
                'title_en': 'Templates',
                'review_state': 'templatefolder-state-active',
                '_permissions': {
                    'read': [
                        'fa_users',
                        'rk_users',
                    ],
                    'edit': [
                        'fa_inbox_users',
                        'rk_inbox_users',
                    ],
                    'add': [
                        'fa_inbox_users',
                        'rk_inbox_users',
                    ]},
            }]
        )])
        self.assertEqual(expected, initial_content)
