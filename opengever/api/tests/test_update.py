from ftw.testbrowser import browsing
from opengever.dossier.behaviors.protect_dossier import IProtectDossier
from opengever.testing import IntegrationTestCase
from plone.locking.interfaces import IRefreshableLockable
import json


class TestGeverContentPatch(IntegrationTestCase):

    @browsing
    def test_extend_locked_error_with_translation(self, browser):
        self.login(self.administrator)
        IRefreshableLockable(self.dossier, None).lock()

        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(code=403):
            browser.open(self.dossier,
                         data=json.dumps({'title': 'New title'}),
                         method='PATCH', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_resource_locked',
             u'translated_message': u'Resource is locked.',
             u'type': u'Forbidden'},
            browser.json)
