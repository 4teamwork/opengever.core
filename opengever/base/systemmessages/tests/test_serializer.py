from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
import pytz


class TestSystemMessageSerializer(IntegrationTestCase):

    def setUp(self):
        super(TestSystemMessageSerializer, self).setUp()
        self.now = datetime(2024, 3, 25, 12, 12, tzinfo=pytz.utc)

    def test_system_message_serializer(self):
        self.login(self.manager)

        with freeze(self.now):
            sys_msg = create(Builder('system_message').having(
                admin_unit=get_current_admin_unit(),
                start_ts=self.now,
                type="warning")
            )
            session = create_session()
            session.add(sys_msg)
            session.flush()

        expected = {
            '@id': 'http://nohost/plone/@system-messages/1',
            '@type': 'virtual.ogds.systemmessage',
            'admin_unit': 'plone',
            'end_ts': '2024-03-28T12:12:00+00:00',
            'id': 1,
            'start_ts': '2024-03-25T12:12:00+00:00',
            'text': 'English message',
            'text_de': 'Deutsch message ',
            'text_en': 'English message',
            'text_fr': 'French message',
            'type': 'warning',
            'active': False
        }
        serializer = getMultiAdapter((sys_msg, getRequest()), ISerializeToJson)
        self.assertEqual(expected, serializer())
