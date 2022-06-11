from mock import Mock
from opengever.contact.browser.contacts_tab import linked
from opengever.contact.browser.contacts_tab import linked_no_icon
from unittest import TestCase


class MockItem(object):
    pass


class TestUnitLinked(TestCase):

    def test_linked_with_unicode_value(self):
        self.assertEqual(
            u'<span class="linkWrapper"><a href="#">f\xfc\xfc</a></span>',
            linked(None, u'f\xfc\xfc')
        )

    def test_linked_with_bytestring_value(self):
        self.assertEqual(
            u'<span class="linkWrapper"><a href="#">f\xfc\xfc</a></span>',
            linked(None, u'f\xfc\xfc'.encode('utf-8'))
        )

    def test_linked_with_bytestring_url(self):
        item = MockItem()
        item.getURL = Mock(return_value=u'http://example.com/fo\xfc'.encode('utf-8'))
        item.css_icon_class = 'bar'
        self.assertEqual(
            u'<span class="linkWrapper bar"><a href="http://example.com/fo\xfc">qux</a></span>',
            linked(item, u'qux')
        )

    def test_linked_with_unicode_url(self):
        item = MockItem()
        item.getURL = Mock(return_value=u'http://example.com/fo\xfc')
        self.assertEqual(
            u'<span class="linkWrapper"><a href="http://example.com/fo\xfc">bar</a></span>',
            linked(item, u'bar')
        )


class TestUnitLinkedNoIcon(TestCase):

    def test_linked_no_icon_with_unicode_value(self):
        self.assertEqual(
            u'<span class="linkWrapper"><a href="#">f\xfc\xfc</a></span>',
            linked_no_icon(None, u'f\xfc\xfc')
        )

    def test_linked_no_icon_with_bytestring_value(self):
        self.assertEqual(
            u'<span class="linkWrapper"><a href="#">f\xfc\xfc</a></span>',
            linked_no_icon(None, u'f\xfc\xfc'.encode('utf-8'))
        )

    def test_linked_no_icon_with_bytestring_url(self):
        item = MockItem()
        item.getURL = Mock(return_value=u'http://example.com/fo\xfc'.encode('utf-8'))
        self.assertEqual(
            u'<span class="linkWrapper"><a href="http://example.com/fo\xfc">quux</a></span>',
            linked_no_icon(item, 'quux')
        )

    def test_linked_no_icon_with_unicode_url(self):
        item = MockItem()
        item.getURL = Mock(return_value=u'http://example.com/fo\xfc')
        self.assertEqual(
            u'<span class="linkWrapper"><a href="http://example.com/fo\xfc">baz</a></span>',
            linked_no_icon(item, u'baz')
        )
