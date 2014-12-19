from datetime import date
from datetime import datetime
from datetime import timedelta
from opengever.ogds.base.utils import CookieStorage
from opengever.testing import FunctionalTestCase


class TestCookieStorage(FunctionalTestCase):
    use_default_fixture = False

    def setUp(self):
        super(TestCookieStorage, self).setUp()

        self.request = self.portal.REQUEST
        self.storage = CookieStorage(self.request)

    def test_getter(self):
        self.request.cookies['foo'] = 'peter'

        self.assertEquals('peter', self.storage.get('foo'))
        self.assertEquals(None, self.storage.get('bar'))

    def test_setter_set_value_on_request_and_response(self):
        self.storage['foo'] = 'bar'

        self.assertEquals({'foo': 'bar'}, self.request.cookies)
        self.assertDictContainsSubset(
            {'quoted': True, 'value': 'bar'},
            self.request.RESPONSE.cookies['foo'])

    def test_sets_cookie_expiration_date(self):
        self.storage['foo'] = 'bar'
        expires = self.request.RESPONSE.cookies['foo']['expires']
        expiry_date = datetime.strptime(expires, "%a, %d-%b-%Y %H:%M:%S GMT")
        self.assertEquals(date.today() + timedelta(days=30), expiry_date.date())

    def test_deleter(self):
        self.request.cookies['foo'] = 'peter'
        self.request.cookies['bar'] = 'hugo'

        del self.storage['bar']

        self.assertEquals({'foo': 'peter'}, self.request.cookies)

    def test_keys(self):
        self.request.cookies['foo'] = 'peter'
        self.request.cookies['bar'] = 'hugo'

        self.assertEquals(['foo', 'bar'], self.storage.keys())
