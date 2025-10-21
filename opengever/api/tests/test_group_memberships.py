from ftw.testbrowser import browsing
from opengever.base.model import create_session
from opengever.ogds.models.group_membership import GroupMembership
from opengever.testing import IntegrationTestCase
import json


class TestMembershipNotesPost(IntegrationTestCase):

    def setUp(self):
        super(TestMembershipNotesPost, self).setUp()

        self.groupid = "projekt_a"
        self.userid = self.regular_user.getId()
        self.session = create_session()

        self.membership = (
            self.session.query(GroupMembership)
            .filter(
                GroupMembership.groupid == self.groupid,
                GroupMembership.userid == self.userid,
            )
            .one()
        )

    @browsing
    def test_note_addition_is_allowed_for_administrators(self, browser):
        self.login(self.regular_user, browser)

        payload = {
            "groupid": self.groupid,
            "userid": self.userid,
            "note": "Example Note",
        }

        with browser.expect_unauthorized():
            browser.open(
                self.portal,
                view="@membership-notes",
                data=json.dumps(payload),
                method="POST",
                headers=self.api_headers,
            )

        self.login(self.administrator, browser)
        response = browser.open(
            self.portal,
            view="@membership-notes",
            data=json.dumps(payload),
            method="POST",
            headers=self.api_headers,
        )

        self.assertEqual(200, response.status_code)
        self.assertDictEqual(
            {"groupid": self.groupid, "userid": self.userid, "note": "Example Note"},
            response.json,
        )
