from opengever.propertysheets.default_expression import tales_expr_default_factory
from opengever.testing import IntegrationTestCase
from plone import api


class TestTalesExpressionDefaultFactory(IntegrationTestCase):

    def test_factory_expr_context_contains_member_if_logged_in(self):
        self.login(self.regular_user)

        self.assertEqual(
            api.user.get_current(),
            tales_expr_default_factory('member'))

        self.assertEqual(
            self.regular_user.id,
            tales_expr_default_factory('member/getId'))

    def test_factory_expr_context_contains_none_member_if_anonymous(self):
        self.assertIsNone(tales_expr_default_factory('member'))

    def test_factory_expr_context_contains_portal(self):
        self.login(self.regular_user)

        self.assertEqual(
            u'Plone site',
            tales_expr_default_factory('portal/title'))

        self.assertEqual(
            'plone',
            tales_expr_default_factory('portal/id'))

    def test_factory_expr_context_contains_portal_url(self):
        self.login(self.regular_user)

        self.assertEqual(
            self.portal.absolute_url(),
            tales_expr_default_factory('portal_url'))

    def test_factory_expr_context_doesnt_contain_object_or_folder(self):
        self.login(self.regular_user)

        # These aren't available because PropertySheet z3c.form widgets
        # currently aren't context aware. `folder` needs to be set to
        # something with an .absolute_url(), so we set it to the portal.
        self.assertIsNone(tales_expr_default_factory('object'))
        self.assertIsNone(tales_expr_default_factory('here'))

        self.assertEqual(
            self.portal.id,
            tales_expr_default_factory('folder/id'))

        self.assertEqual(
            self.portal.absolute_url(),
            tales_expr_default_factory('folder_url'))

    def test_factory_expr_context_contains_request(self):
        self.assertEqual(
            self.request,
            tales_expr_default_factory('request'))

    def test_factory_expr_context_contains_none_as_nothing(self):
        self.assertIsNone(tales_expr_default_factory('nothing'))

    def test_doesnt_choke_on_invalid_expression(self):
        self.assertIsNone(tales_expr_default_factory('/|'))

    def test_doesnt_choke_on_nonexistent_ec_key(self):
        self.assertIsNone(tales_expr_default_factory('doesntexist/foo'))

    def test_doesnt_choke_on_nonexistent_attribute(self):
        self.assertIsNone(tales_expr_default_factory('portal/doesntexist'))
