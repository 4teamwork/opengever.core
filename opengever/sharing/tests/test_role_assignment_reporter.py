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
                            "@id": "http://nohost/plone/ordnungssystem/rechnungsprufungskommission"
                        },
                        "role_assignments": {"Contributor": ["archivist"], "Publisher": ["archivist"]},
                    },
                    {
                        "item": {"@id": "http://nohost/plone/workspaces/workspace-1"},
                        "role_assignments": {
                            "WorkspaceAdmin": ["fridolin.hugentobler", "gunther.frohlich"],
                            "WorkspaceGuest": ["hans.peter"],
                            "WorkspaceMember": ["beatrice.schrodinger"],
                        },
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
            }, reporter('jurgen.konig'))

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
                            "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-17",
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
                ],
            },
            self.strip_item_metadata(reporter('jurgen.konig', include_memberships=True)))

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
