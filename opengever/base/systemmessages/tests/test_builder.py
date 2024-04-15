from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.base.systemmessages.api.schemas import ISystemMessageAPISchema
from opengever.testing import IntegrationTestCase
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
import json
import pytz


class TestSystemMessageBuilder(IntegrationTestCase):

    @browsing
    def test_builder_creates_valid_system_message(self, browser):
        self.login(self.manager, browser=browser)

        now = datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)
        with freeze(now):
            sys_msg = create(Builder('system_message'))
            session = create_session()
            session.add(sys_msg)
            session.flush()

        serialized = getMultiAdapter((sys_msg, getRequest()), ISerializeToJson)()

        readonly = set(serialized.keys()) - set(ISystemMessageAPISchema.names())
        for field in readonly:
            serialized.pop(field)

        with freeze(now):
            browser.open(self.portal, view='@system-messages', method='POST',
                         data=json.dumps(serialized),
                         headers=self.api_headers)

        self.assertEqual(201, browser.status_code)
