from ftw.testbrowser import browsing
from opengever.sharing.security import disabled_permission_check
from opengever.testing import IntegrationTestCase
from plone.restapi.interfaces import ISerializeToJson
from zope.component import queryMultiAdapter


class TestLocalRolesSerializer(IntegrationTestCase):

    @browsing
    def test_local_roles_are_batched_if_searching(self, browser):
        self.login(self.regular_user, browser=browser)

        self.request.form['b_size'] = 3
        serializer = queryMultiAdapter((self.dossier, self.request),
                                       interface=ISerializeToJson,
                                       name='local_roles')

        with disabled_permission_check():
            result = serializer(search="A")
        self.assertEqual(27, result['items_total'])
        self.assertEqual(3, len(result['items']))
        self.assertIn('batching', result)

    @browsing
    def test_local_roles_are_not_batched_if_not_searching(self, browser):
        self.login(self.regular_user, browser=browser)

        self.request.form['b_size'] = 3
        serializer = queryMultiAdapter((self.dossier, self.request),
                                       interface=ISerializeToJson,
                                       name='local_roles')

        with disabled_permission_check():
            result = serializer()

        self.assertEqual(6, len(result['entries']))
        self.assertNotIn('batching', result)
