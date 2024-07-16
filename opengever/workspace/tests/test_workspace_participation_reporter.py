from ftw.builder.builder import Builder
from ftw.builder.builder import create
from ftw.testbrowser import browsing
from opengever.ogds.models.service import ogds_service
from opengever.testing import IntegrationTestCase
from openpyxl import load_workbook
from tempfile import NamedTemporaryFile


class TestWorkspaceParticipationReporter(IntegrationTestCase):

    @browsing
    def test_empty_users_report(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(view='workspace_participants_report', data={'user_ids': []})

        self.assertEquals('Error You have not selected any items.',
                          browser.css('.portalMessage.error').text[0])

    @browsing
    def test_download_users_xlsx(self, browser):
        """Test downloading a user report in XLSX format.
        This test verifies that the user report correctly generates an XLSX file
        including individual users and users within a group.
        """
        self.login(self.administrator, browser=browser)

        # Create a group and add regular_user to the group
        group_users = ogds_service().find_user(self.regular_user.id)
        group = create(Builder('ogds_group')
                       .having(groupid='group1',
                               title='Group 1', users=[group_users, ]))

        user_ids = {
            'user_ids': [
                self.regular_user.id,
                self.administrator.id,
                group.groupid
            ]
        }

        browser.open(view='workspace_participants_report', data=user_ids)
        self.assertEqual(browser.status_code, 200)
        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(browser.contents)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

        task_cells = list(workbook.active.rows)

        # if ror_num != 0 will remove the table header
        cell_values = [[cell.value for cell in row] for row_num, row in enumerate(task_cells) if row_num != 0]
        expected_values = [
            [
                u'kathi.barfuss',
                True,
                u'K\xe4thi',
                u'B\xe4rfuss',
                u'B\xe4rfuss K\xe4thi',
                u'Staatsarchiv',
                u'Arch',
                u'Staatskanzlei',
                u'SK',
                None,
                u'foo@example.com',
                u'bar@example.com',
                u'http://www.example.com',
                u'012 34 56 78',
                u'012 34 56 77',
                u'012 34 56 76',
                u'Frau',
                u'Gesch\xe4ftsf\xfchrerin',
                u'nix',
                u'Kappelenweg 13',
                u'Postfach 1234',
                u'1234',
                u'Vorkappelen',
                u'Schweiz',
                None
            ],
            [
                u'nicole.kohler',
                True,
                u'Nicole',
                u'Kohler',
                u'Kohler Nicole',
                None,
                None,
                None,
                None,
                None,
                u'nicole.kohler@gever.local',
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None
            ]
        ]
        self.assertItemsEqual(expected_values, cell_values)
