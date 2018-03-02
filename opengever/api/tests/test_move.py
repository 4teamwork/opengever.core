from ftw.testbrowser import browsing
from plone.app.testing import setRoles
from opengever.testing import IntegrationTestCase
import json


class TestMove(IntegrationTestCase):

    def setUp(self):
        super(TestMove, self).setUp()

    @browsing
    def test_regular_user_can_move_document(self, browser):
        self.login(self.regular_user, browser)
        setRoles(self.portal, self.regular_user.getId(), ['APIUser'])
        doc_id = self.document.getId()
        browser.open(
            self.subdossier.absolute_url() + '/@move',
            data=json.dumps({"source": self.document.absolute_url()}),
            method='POST',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'},
        )
        self.assertEqual(200, browser.status_code)
        self.assertIn(doc_id, self.subdossier)
