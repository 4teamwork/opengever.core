from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
from unittest2 import TestCase


class TestUnitMember(TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestUnitMember, self).setUp()
        self.session = self.layer.session

    def test_string_representation(self):
        member = create(Builder('member').having(
            firstname=u'Peter', lastname=u'M\xfcller'))
        self.assertEqual("<Member u'M\\xfcller Peter'>", str(member))
        self.assertEqual("<Member u'M\\xfcller Peter'>", repr(member))

    def test_get_title_embedds_email_correctly(self):
        member = create(Builder('member').having(
            firstname=u'Peter',
            lastname=u'M\xfcller',
            email=u'm\xf6ller@example.com'))
        self.assertEqual(u'M\xfcller Peter (<a href="mailto:m\xf6ller@example.com">m\xf6ller@example.com</a>)',
                         member.get_title())

    def test_get_title_omits_email_when_required(self):
        member = create(Builder('member').having(
            firstname=u'Peter',
            lastname=u'M\xfcller',
            email=u'm\xf6ller@example.com'))
        self.assertEqual(u'M\xfcller Peter (m\xf6ller@example.com)',
                         member.get_title(show_email_as_link=False))
