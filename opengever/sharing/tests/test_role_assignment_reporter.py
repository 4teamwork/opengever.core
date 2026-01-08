from copy import deepcopy
from opengever.sharing.local_roles_lookup.reporter import RoleAssignmentReporter
from opengever.testing import SolrIntegrationTestCase


class TestRoleAssignmentReporter(SolrIntegrationTestCase):

    def strip_item_metadata(self, report):
        """Formats the report by removing item metadata for easier testing
        """
        formatted_report = deepcopy(report)
        for report_item in formatted_report.get('items'):
            report_item['item'] = {'@id': report_item['item'].get('@id')}

        return formatted_report

    def strip_excel_item_metadata(self, report):
        """Formats the report by removing item metadata for easier testing
        """
        formatted_report = []
        for report_item in report:
            report_item['item'] = {'@id': report_item['item'].get('@id')}
            formatted_report.append(report_item)

        return formatted_report

    def test_can_creates_a_report_for_all_principals_and_objects(self):
        self.login(self.administrator)
        reporter = RoleAssignmentReporter()

        self.assertEqual(
            {
                'total_items': 10,
                'items': [
                    {
                        "item": {"@id": "http://nohost/plone/ordnungssystem"},
                        "role_assignments": {
                            "Contributor": ["archivist", "fa_users"],
                            "Editor": ["fa_users"],
                            "Publisher": ["jurgen.konig"],
                            "Reader": ["fa_users"],
                            "Reviewer": ["jurgen.konig"],
                        },
                    },
                    {
                        "item": {"@id": "http://nohost/plone/workspaces/workspace-1"},
                        "role_assignments": {
                            "WorkspaceAdmin": ["fridolin.hugentobler", "gunther.frohlich"],
                            "WorkspaceGuest": ["hans.peter"],
                            "WorkspaceMember": ["beatrice.schrodinger"],
                        },
                    },
                    {
                        "item": {"@id": "http://nohost/plone/ordnungssystem/fuhrung"},
                        "role_assignments": {"DossierManager": ["dossier_manager"]},
                    },
                    {
                        "item": {
                            "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1"
                        },
                        "role_assignments": {"TaskResponsible": ["fa_inbox_users", "regular_user"]},
                    },
                    {
                        "item": {
                            "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4"
                        },
                        "role_assignments": {
                            "Editor": ["archivist"],
                            "Reader": ["archivist"],
                            "Reviewer": ["archivist"],
                        },
                    },
                    {
                        "item": {
                            "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-5"
                        },
                        "role_assignments": {"TaskResponsible": ["fa_inbox_users", "regular_user"]},
                    },
                    {
                        "item": {
                            "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-6"
                        },
                        "role_assignments": {"TaskResponsible": ["fa_inbox_users", "regular_user"]},
                    },
                    {
                        "item": {
                            "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-16"
                        },
                        "role_assignments": {
                            "Contributor": ["robert.ziegler"],
                            "Editor": ["robert.ziegler"],
                            "Reader": ["robert.ziegler"],
                        },
                    },
                    {
                        "item": {
                            "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-17"
                        },
                        "role_assignments": {
                            "Contributor": ["robert.ziegler"],
                            "Editor": ["robert.ziegler"],
                            "Reader": ["robert.ziegler"],
                            "TaskResponsible": ["fa_inbox_users", "regular_user"],
                        },
                    },
                    {
                        "item": {
                            "@id": "http://nohost/plone/ordnungssystem/rechnungsprufungskommission"
                        },
                        "role_assignments": {"Contributor": ["archivist"], "Publisher": ["archivist"]},
                    },
                ]
            }, self.strip_item_metadata(reporter()))

    def test_creates_a_report_for_a_single_principal(self):
        self.login(self.administrator)
        reporter = RoleAssignmentReporter()

        self.assertEqual(
            {
                'total_items': 1,
                'items': [
                    {
                        'item': {
                            '@id': 'http://nohost/plone/ordnungssystem',
                            '@type': 'opengever.repository.repositoryroot',
                            'UID': 'createrepositorytree000000000001',
                            'description': '',
                            'is_leafnode': None,
                            'reference': 'Client1',
                            'review_state': 'repositoryroot-state-active',
                            'title': 'Ordnungssystem'
                        },
                        'role_assignments': {
                            'Publisher': ['jurgen.konig'],
                            'Reviewer': ['jurgen.konig']
                        }
                    }
                ],
            }, reporter(['jurgen.konig']))

    def test_creates_a_report_for_multiple_principals(self):
        self.login(self.administrator)
        reporter = RoleAssignmentReporter()

        self.assertEqual(
            {
                "total_items": 3,
                "items": [
                    {
                        "item": {
                            "@id": "http://nohost/plone/ordnungssystem",
                            "@type": "opengever.repository.repositoryroot",
                            "UID": "createrepositorytree000000000001",
                            "description": "",
                            "is_leafnode": None,
                            "reference": "Client1",
                            "review_state": "repositoryroot-state-active",
                            "title": "Ordnungssystem",
                        },
                        "role_assignments": {
                            "Contributor": ["archivist"],
                            "Reviewer": ["jurgen.konig"],
                            "Publisher": ["jurgen.konig"],
                        },
                    },
                    {
                        "item": {
                            "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4",
                            "@type": "opengever.dossier.businesscasedossier",
                            "UID": "createtreatydossiers000000000018",
                            "description": "",
                            "is_leafnode": None,
                            "reference": "Client1 1.1 / 1.1.1",
                            "review_state": "dossier-state-active",
                            "title": "Subsubdossier",
                        },
                        "role_assignments": {
                            "Reviewer": ["archivist"],
                            "Editor": ["archivist"],
                            "Reader": ["archivist"],
                        },
                    },
                    {
                        "item": {
                            "@id": "http://nohost/plone/ordnungssystem/rechnungsprufungskommission",
                            "@type": "opengever.repository.repositoryfolder",
                            "UID": "createrepositorytree000000000004",
                            "description": "",
                            "is_leafnode": True,
                            "reference": "Client1 2",
                            "review_state": "repositoryfolder-state-active",
                            "title": "2. Rechnungspr\xc3\xbcfungskommission",
                        },
                        "role_assignments": {
                            "Contributor": ["archivist"],
                            "Publisher": ["archivist"],
                        },
                    },
                ],
            }, reporter(['jurgen.konig', 'archivist']))

    def test_creates_a_report_for_a_principal_including_all_group_memberships(self):
        self.login(self.administrator)
        reporter = RoleAssignmentReporter()

        self.assertEqual(
            {
                'total_items': 5,
                'items': [
                    {
                        "item": {
                            "@id": "http://nohost/plone/ordnungssystem",
                        },
                        "role_assignments": {
                            "Contributor": ["fa_users"],
                            "Editor": ["fa_users"],
                            "Publisher": ["jurgen.konig"],
                            "Reader": ["fa_users"],
                            "Reviewer": ["jurgen.konig"],
                        },
                    },
                    {
                        "item": {
                            "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1",
                        },
                        "role_assignments": {"TaskResponsible": ["fa_inbox_users"]},
                    },
                    {
                        "item": {
                            "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-5",
                        },
                        "role_assignments": {"TaskResponsible": ["fa_inbox_users"]},
                    },
                    {
                        "item": {
                            "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-6",
                        },
                        "role_assignments": {"TaskResponsible": ["fa_inbox_users"]},
                    },
                    {
                        "item": {
                            "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-17",
                        },
                        "role_assignments": {"TaskResponsible": ["fa_inbox_users"]},
                    },
                ],
            },
            self.strip_item_metadata(reporter(['jurgen.konig'], include_memberships=True)))

    def test_creates_a_report_restricted_to_a_specific_branch(self):
        self.login(self.administrator)
        reporter = RoleAssignmentReporter()

        report = reporter(include_memberships=True, root=self.dossier.UID())
        self.assertEqual(
            [
                'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
                'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4',
            ],
            [report_item.get('item').get('@id') for report_item in report.get('items')])

    def test_report_for_is_batched(self):
        self.login(self.administrator)
        reporter = RoleAssignmentReporter()

        report = reporter(rows=3)
        self.assertEqual(3, len(report.get('items')))
        self.assertEqual(10, report.get('total_items'))

    def test_can_creates_an_excel_report_for_all_principals_and_objects(self):
        self.login(self.administrator)
        reporter = RoleAssignmentReporter()
        self.assertEqual(
            [
                {
                    "item": {"@id": "http://nohost/plone/ordnungssystem"},
                    "principal": {
                        "groupname": None,
                        "principal_id": "archivist",
                        "username": "jurgen.fischer",
                    },
                    "role": "Contributor",
                },
                {
                    "item": {"@id": "http://nohost/plone/ordnungssystem"},
                    "principal": {
                        "groupname": "fa_users",
                        "principal_id": "fa_users",
                        "username": None,
                    },
                    "role": "Contributor",
                },
                {
                    "item": {"@id": "http://nohost/plone/ordnungssystem"},
                    "principal": {
                        "groupname": "fa_users",
                        "principal_id": "fa_users",
                        "username": None,
                    },
                    "role": "Editor",
                },
                {
                    "item": {"@id": "http://nohost/plone/ordnungssystem"},
                    "principal": {
                        "groupname": "fa_users",
                        "principal_id": "fa_users",
                        "username": None,
                    },
                    "role": "Reader",
                },
                {
                    "item": {"@id": "http://nohost/plone/ordnungssystem"},
                    "principal": {
                        "groupname": None,
                        "principal_id": "jurgen.konig",
                        "username": "jurgen.konig",
                    },
                    "role": "Reviewer",
                },
            ], self.strip_excel_item_metadata(reporter.excel_report_for())[:5])

    def test_can_creates_an_excel_report_for_a_single_principal(self):
        self.login(self.administrator)
        reporter = RoleAssignmentReporter()
        self.assertEqual(
            [
                {
                    "item": {"@id": "http://nohost/plone/ordnungssystem"},
                    "principal": {
                        "groupname": None,
                        "principal_id": "jurgen.konig",
                        "username": "jurgen.konig",
                    },
                    "role": "Reviewer",
                },
                {
                    "item": {"@id": "http://nohost/plone/ordnungssystem"},
                    "principal": {
                        "groupname": None,
                        "principal_id": "jurgen.konig",
                        "username": "jurgen.konig",
                    },
                    "role": "Publisher",
                },
            ], self.strip_excel_item_metadata(reporter.excel_report_for(['jurgen.konig'])))

    def test_can_creates_an_excel_report_for_a_principal_including_all_group_memberships(self):
        self.login(self.administrator)
        reporter = RoleAssignmentReporter()
        self.assertEqual(
            [
                {
                    "item": {"@id": "http://nohost/plone/ordnungssystem"},
                    "principal": {
                        "groupname": "fa_users",
                        "principal_id": "fa_users",
                        "username": None,
                    },
                    "role": "Contributor",
                },
                {
                    "item": {"@id": "http://nohost/plone/ordnungssystem"},
                    "principal": {
                        "groupname": "fa_users",
                        "principal_id": "fa_users",
                        "username": None,
                    },
                    "role": "Editor",
                },
                {
                    "item": {"@id": "http://nohost/plone/ordnungssystem"},
                    "principal": {
                        "groupname": "fa_users",
                        "principal_id": "fa_users",
                        "username": None,
                    },
                    "role": "Reader",
                },
                {
                    "item": {"@id": "http://nohost/plone/ordnungssystem"},
                    "principal": {
                        "groupname": None,
                        "principal_id": "jurgen.konig",
                        "username": "jurgen.konig",
                    },
                    "role": "Reviewer",
                },
                {
                    "item": {"@id": "http://nohost/plone/ordnungssystem"},
                    "principal": {
                        "groupname": None,
                        "principal_id": "jurgen.konig",
                        "username": "jurgen.konig",
                    },
                    "role": "Publisher",
                },
                {
                    "item": {
                        "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1"
                    },
                    "principal": {
                        "groupname": "fa_inbox_users",
                        "principal_id": "fa_inbox_users",
                        "username": None,
                    },
                    "role": "TaskResponsible",
                },
                {
                    "item": {
                        "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-5"
                    },
                    "principal": {
                        "groupname": "fa_inbox_users",
                        "principal_id": "fa_inbox_users",
                        "username": None,
                    },
                    "role": "TaskResponsible",
                },
                {
                    "item": {
                        "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-6"
                    },
                    "principal": {
                        "groupname": "fa_inbox_users",
                        "principal_id": "fa_inbox_users",
                        "username": None,
                    },
                    "role": "TaskResponsible",
                },
                                {
                    "item": {
                        "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-17"
                    },
                    "principal": {
                        "groupname": "fa_inbox_users",
                        "principal_id": "fa_inbox_users",
                        "username": None,
                    },
                    "role": "TaskResponsible",
                },
            ],
            self.strip_excel_item_metadata(reporter.excel_report_for(
                ['jurgen.konig'], include_memberships=True)))

    def test_can_creates_an_excel_report_restricted_to_a_specific_branch(self):
        self.login(self.administrator)
        reporter = RoleAssignmentReporter()
        self.assertEqual(
            [
                {
                    "item": {
                        "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1"
                    },
                    "principal": {
                        "groupname": "fa_inbox_users",
                        "principal_id": "fa_inbox_users",
                        "username": None,
                    },
                    "role": "TaskResponsible",
                },
                {
                    "item": {
                        "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1"
                    },
                    "principal": {
                        "groupname": None,
                        "principal_id": "regular_user",
                        "username": "kathi.barfuss",
                    },
                    "role": "TaskResponsible",
                },
                {
                    "item": {
                        "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4"
                    },
                    "principal": {
                        "groupname": None,
                        "principal_id": "archivist",
                        "username": "jurgen.fischer",
                    },
                    "role": "Reviewer",
                },
                {
                    "item": {
                        "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4"
                    },
                    "principal": {
                        "groupname": None,
                        "principal_id": "archivist",
                        "username": "jurgen.fischer",
                    },
                    "role": "Editor",
                },
                {
                    "item": {
                        "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4"
                    },
                    "principal": {
                        "groupname": None,
                        "principal_id": "archivist",
                        "username": "jurgen.fischer",
                    },
                    "role": "Reader",
                },
            ],
            self.strip_excel_item_metadata(reporter.excel_report_for(root=self.dossier.UID())))
