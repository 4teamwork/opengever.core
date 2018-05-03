from opengever.oneoffixx.connector import OneOffixConnector
from opengever.testing import IntegrationTestCase


def mocked_get_template_groups(self):
    return [
        {'templates': [
            {u'languages': [2055],
             u'localizedName': u'Brief schwarz/weiss',
             u'templateGroupId': u'14ff1ebc-ba0c-4732-93e2-829fe6cc6bc6',
             u'id': u'52945b6c-b65a-436d-8045-619e4e41af51'},
            {u'languages': [2055],
             u'localizedName': u'Brief farbig',
             u'templateGroupId': u'14ff1ebc-ba0c-4732-93e2-829fe6cc6bc6',
             u'id': u'06149cd5-efe1-47e5-a822-993fa1b65ef0'},
            {u'languages': [2055],
             u'localizedName': u'Kurzbrief',
             u'templateGroupId': u'14ff1ebc-ba0c-4732-93e2-829fe6cc6bc6',
             u'id': u'2574d08d-95ea-4639-beab-3103fe4c3bc7'},
        ],
                  u'id':u'14ff1ebc-ba0c-4732-93e2-829fe6cc6bc6',
         u'localizedName': u'Korrespondenz'
     },
                 {'templates': [
                     {u'languages': [2055],
                      u'localizedName': u'Entwurf Bericht/Botschaft',
                      u'templateGroupId': u'3a66d83c-077c-4917-aef6-6d4765af1126',
                      u'id': u'8b82b8c1-6780-4c5c-8229-00da90f96b15'},
                     {u'languages': [2055],
                      u'localizedName': u'Antwort Vorstoss',
                      u'templateGroupId': u'3a66d83c-077c-4917-aef6-6d4765af1126',
                      u'id': u'810b1174-f12e-4e43-959e-d5fda1e7f0e2'},
                 ],
                  u'id': u'3a66d83c-077c-4917-aef6-6d4765af1126',
                  u'localizedName': u'Kantonsrat'
              }]


class OneOffixIntegrationTests(IntegrationTestCase):
    features = ("officeconnector-checkout", "oneoffixx")

    def setUp(self):
        super(OneOffixIntegrationTests, self).setUp()
        self.org_method = OneOffixConnector.get_template_groups
        OneOffixConnector.get_template_groups = mocked_get_template_groups

    def tearDown(self):
        OneOffixConnector.get_template_groups = self.org_method
        super(OneOffixIntegrationTests, self).tearDown()
