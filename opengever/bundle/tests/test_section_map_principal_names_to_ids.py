from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.base.model import create_session
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.bundle.sections.map_principal_names_to_ids import AmbiguousPrincipalNames
from opengever.bundle.sections.map_principal_names_to_ids import MapPrincipalNamesToIDsSection
from opengever.bundle.tests import MockBundle
from opengever.bundle.tests import MockTransmogrifier
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from opengever.testing import IntegrationTestCase
from uuid import uuid4
from zope.annotation import IAnnotations
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class TestMapPrincipalNamesToIDs(IntegrationTestCase):

    def setUp(self):
        super(TestMapPrincipalNamesToIDs, self).setUp()
        self.session = create_session()

    def setup_section(self, previous=None):
        previous = previous or []
        transmogrifier = MockTransmogrifier()
        self.bundle = MockBundle()
        IAnnotations(transmogrifier)[BUNDLE_KEY] = self.bundle

        options = {'blueprint': 'opengever.bundle.map_principal_names_to_ids'}

        return MapPrincipalNamesToIDsSection(transmogrifier, '', options, previous)

    def test_implements_interface(self):
        self.assertTrue(ISection.implementedBy(MapPrincipalNamesToIDsSection))
        verifyClass(ISection, MapPrincipalNamesToIDsSection)

        self.assertTrue(ISectionBlueprint.providedBy(MapPrincipalNamesToIDsSection))
        verifyObject(ISectionBlueprint, MapPrincipalNamesToIDsSection)

    def test_maps_usernames_to_userids(self):
        user1 = User(
            userid='11111',
            username='user1',
            external_id=uuid4().hex,
        )
        user2 = User(
            userid='22222',
            username='user2',
            external_id=uuid4().hex,
        )
        user3 = User(
            userid='33333',
            username='user3',
            external_id=uuid4().hex,
        )
        user4 = User(
            userid='44444',
            username='user4',
            external_id=uuid4().hex,
        )
        user5 = User(
            userid='55555',
            username='user5',
            external_id=uuid4().hex,
        )

        for user in (user1, user2, user3, user4, user5):
            self.session.add(user)
        self.session.flush()

        items = [
            {
                'guid': 'mapped-users',
                '_type': 'opengever.dossier.businesscasedossier',
                '_permissions': {
                    'read': ['user1'],
                    'add': ['user2'],
                    'edit': ['user3'],
                    'close': ['user4'],
                    'reactivate': ['user5'],
                },
            },

        ]
        section = self.setup_section(previous=items)
        transformed_items = list(section)

        expected = [
            {
                'guid': 'mapped-users',
                '_type': 'opengever.dossier.businesscasedossier',
                '_permissions': {
                    'read': [user1.userid],
                    'add': [user2.userid],
                    'edit': [user3.userid],
                    'close': [user4.userid],
                    'reactivate': [user5.userid],
                },
            },

        ]

        self.assertEquals(expected, transformed_items)

    def test_maps_groupnames_to_groupids(self):
        group1 = Group(
            groupid='11111',
            groupname='group1',
            external_id=uuid4().hex,
        )
        group2 = Group(
            groupid='22222',
            groupname='group2',
            external_id=uuid4().hex,
        )
        group3 = Group(
            groupid='33333',
            groupname='group3',
            external_id=uuid4().hex,
        )
        group4 = Group(
            groupid='44444',
            groupname='group4',
            external_id=uuid4().hex,
        )
        group5 = Group(
            groupid='55555',
            groupname='group5',
            external_id=uuid4().hex,
        )

        for group in (group1, group2, group3, group4, group5):
            self.session.add(group)
        self.session.flush()

        items = [
            {
                'guid': 'mapped-groups',
                '_type': 'opengever.dossier.businesscasedossier',
                '_permissions': {
                    'read': ['group1'],
                    'add': ['group2'],
                    'edit': ['group3'],
                    'close': ['group4'],
                    'reactivate': ['group5'],
                },
            },

        ]
        section = self.setup_section(previous=items)
        transformed_items = list(section)

        expected = [
            {
                'guid': 'mapped-groups',
                '_type': 'opengever.dossier.businesscasedossier',
                '_permissions': {
                    'read': [group1.groupid],
                    'add': [group2.groupid],
                    'edit': [group3.groupid],
                    'close': [group4.groupid],
                    'reactivate': [group5.groupid],
                },
            },

        ]

        self.assertEquals(expected, transformed_items)

    def test_leaves_unapped_principal_names_unchanged(self):
        items = [
            {
                'guid': 'unmapped-principals',
                '_type': 'opengever.dossier.businesscasedossier',
                '_permissions': {
                    'read': ['john.doe'],
                    'add': ['admin_users'],
                    'edit': ['admin_users', 'afi_users'],
                    'close': ['admin_users'],
                    'reactivate': ['admin_users'],
                },
            },

        ]
        section = self.setup_section(previous=items)
        transformed_items = list(section)

        self.assertEquals(items, transformed_items)

    def test_groups_take_precedence_over_users(self):
        group1 = Group(
            groupid='11111',
            groupname='one',
            external_id=uuid4().hex,
        )
        user1 = User(
            userid='22222',
            username='one',
            external_id=uuid4().hex,
        )

        for obj in (group1, user1):
            self.session.add(obj)
        self.session.flush()

        items = [
            {
                'guid': 'mapped-groups',
                '_type': 'opengever.dossier.businesscasedossier',
                '_permissions': {
                    'read': ['one'],
                },
            },

        ]
        section = self.setup_section(previous=items)
        transformed_items = list(section)

        expected = [
            {
                'guid': 'mapped-groups',
                '_type': 'opengever.dossier.businesscasedossier',
                '_permissions': {
                    'read': [group1.groupid],
                },
            },

        ]

        self.assertEquals(expected, transformed_items)

    def test_mapping_is_case_insensitive(self):
        group1 = Group(
            groupid='11111',
            groupname='GROUP1',
            external_id=uuid4().hex,
        )
        group2 = Group(
            groupid='22222',
            groupname='group2',
            external_id=uuid4().hex,
        )

        for group in (group1, group2):
            self.session.add(group)
        self.session.flush()

        items = [
            {
                'guid': 'mapped-groups',
                '_type': 'opengever.dossier.businesscasedossier',
                '_permissions': {
                    'read': ['group1'],
                    'add': ['GROUP1'],
                    'edit': ['group2'],
                    'close': ['GROUP2'],
                },
            },

        ]
        section = self.setup_section(previous=items)
        transformed_items = list(section)

        expected = [
            {
                'guid': 'mapped-groups',
                '_type': 'opengever.dossier.businesscasedossier',
                '_permissions': {
                    'read': [group1.groupid],
                    'add': [group1.groupid],
                    'edit': [group2.groupid],
                    'close': [group2.groupid],
                },
            },

        ]

        self.assertEquals(expected, transformed_items)

    def test_only_active_ogds_principals_are_considered(self):
        inactive_group = Group(
            groupid='inactive-11111',
            groupname='group1',
            external_id=uuid4().hex,
            active=False,
        )
        inactive_user = User(
            userid='inactive-22222',
            username='user1',
            external_id=uuid4().hex,
            active=False,
        )

        for principal in (inactive_group, inactive_user):
            self.session.add(principal)
        self.session.flush()

        items = [
            {
                'guid': 'mapped-groups',
                '_type': 'opengever.dossier.businesscasedossier',
                '_permissions': {
                    'read': ['group1'],
                    'add': ['user1'],
                },
            },

        ]
        section = self.setup_section(previous=items)
        transformed_items = list(section)

        expected = [
            {
                'guid': 'mapped-groups',
                '_type': 'opengever.dossier.businesscasedossier',
                '_permissions': {
                    'read': ['group1'],
                    'add': ['user1'],
                },
            },

        ]

        self.assertEquals(expected, transformed_items)

    def test_raises_on_ambiguous_names_in_ogds(self):
        lower_group = Group(
            groupid='11111',
            groupname='group1',
            external_id=uuid4().hex,
        )
        upper_group = Group(
            groupid='22222',
            groupname='GROUP1',
            external_id=uuid4().hex,
        )

        lower_user = User(
            userid='33333',
            username='user1',
            external_id=uuid4().hex,
        )
        upper_user = User(
            userid='44444',
            username='USER1',
            external_id=uuid4().hex,
        )

        for obj in (lower_group, upper_group, lower_user, upper_user):
            self.session.add(obj)
        self.session.flush()

        items = [
            {
                'guid': 'mapped-groups',
                '_type': 'opengever.dossier.businesscasedossier',
                '_permissions': {
                    'read': ['group1'],
                    'add': ['user1'],
                },
            },

        ]

        with self.assertRaises(AmbiguousPrincipalNames):
            section = self.setup_section(previous=items)
            list(section)
