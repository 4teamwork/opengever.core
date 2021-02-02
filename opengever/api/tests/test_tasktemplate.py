from ftw.testbrowser import browsing
from opengever.ogds.base.actor import INTERACTIVE_ACTOR_RESPONSIBLE_ID
from opengever.testing import SolrIntegrationTestCase
import json


class TestTaskTemplatePost(SolrIntegrationTestCase):

    @browsing
    def test_tasktemplate_responsible_has_a_responsible_client(self, browser):
        self.login(self.administrator, browser=browser)

        data = {
            '@type': u'opengever.tasktemplates.tasktemplate',
            'title': 'Testtasktemplate',
            'task_type': {'token': 'information'},
            'deadline': 7,
            'issuer': {'token': INTERACTIVE_ACTOR_RESPONSIBLE_ID},
            "responsible": {
                'token': "fa:{}".format(self.secretariat_user.id),
                'title': u'Finanzamt: K\xe4thi B\xe4rfuss'
            },
        }

        browser.open(self.tasktemplatefolder, method="POST",
                     headers=self.api_headers, data=json.dumps(data))

        self.assertEquals(
            {u'title': u'Finanz\xe4mt: K\xf6nig J\xfcrgen (jurgen.konig)', u'token': u'fa:jurgen.konig'},
            browser.json.get('responsible'))
        self.assertEquals({u'title': u'Finanz\xe4mt', u'token': u'fa'},
                          browser.json.get('responsible_client'))
