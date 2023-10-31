from opengever.propertysheets.default_from_member import member_property_default_factory
from opengever.testing import IntegrationTestCase
from plone import api
import json


class TestDefaultFromMemberDefaultFactory(IntegrationTestCase):

    def test_returns_member_property(self):
        self.login(self.regular_user)

        self.assertEqual(
            u'foo@example.com',
            member_property_default_factory(
                json.dumps({'property': 'email'})))

    def test_returns_member_property_with_mapping_applied(self):
        self.login(self.regular_user)

        self.assertEqual(
            u'FOO@EXAMPLE.COM',
            member_property_default_factory(
                json.dumps({
                    'property': 'email',
                    'mapping': {
                        u'foo@example.com': u'FOO@EXAMPLE.COM',
                    }
                })))

    def test_mapping_handles_unicode_vs_bytestring(self):
        self.login(self.regular_user)

        self.assertEqual(
            u'Kat',
            member_property_default_factory(
                json.dumps({    
                    'property': 'fullname',
                    'mapping': {
                        u'B\xe4rfuss K\xe4thi': u'Kat',
                    }
                })))

        self.assertEqual(
            u'Kat',
            member_property_default_factory(
                json.dumps({
                    'property': 'fullname',
                    'mapping': {
                        'B\xc3\xa4rfuss K\xc3\xa4thi': u'Kat',
                    }
                })))

    def test_honours_fallback_for_nonexistent_property(self):
        self.login(self.regular_user)

        self.assertEqual(
            u'<N/A>',
            member_property_default_factory(
                json.dumps({
                    'property': 'doesntexist',
                    'fallback': u'<N/A>'
                    }
                )))

    def test_honours_fallback_for_falsy_property(self):
        self.login(self.regular_user)

        self.assertEqual(
            u'<No description>',
            member_property_default_factory(
                json.dumps({
                    'property': 'description',
                    'fallback': u'<No description>'
                    }
                )))

    def test_returns_fallback_for_unauthorized_requests(self):
        self.assertEqual(
            u'<No description>',
            member_property_default_factory(
                json.dumps({
                    'property': 'description',
                    'fallback': u'<No description>'
                    }
                )))

    def test_uses_fallback_for_unmapped_value_by_default(self):
        self.login(self.regular_user)

        self.assertEqual(
            u'FALLBACK',
            member_property_default_factory(
                json.dumps({
                    'property': 'email',
                    'fallback': u'FALLBACK',
                    'mapping': {
                        u'doesnt.match@example.com': u'DOESNT.MATCH@EXAMPLE.COM',
                    }
                })))

    def test_honours_allow_unmapped(self):
        self.login(self.regular_user)

        member = api.user.get_current()

        self.assertEqual(
            member.getProperty('email'),
            member_property_default_factory(
                json.dumps({
                    'property': 'email',
                    'fallback': u'FALLBACK',
                    'allow_unmapped': True,
                    'mapping': {
                        u'doesnt.match@example.com': u'DOESNT.MATCH@EXAMPLE.COM',
                    }
                })))
