from datetime import datetime
from datetime import timedelta
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.base.systemmessages.models import SystemMessage
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
import pytz


class TestSystemMessageModel (IntegrationTestCase):

    def setUp(self):
        super(TestSystemMessageModel, self).setUp()
        self.login(self.regular_user)
        self.now = datetime.now(pytz.utc)

    def test_system_message_creation(self):
        with freeze(self.now):
            sys_msg = SystemMessage(
                admin_unit=get_current_admin_unit(),
                text_en=u'message in en',
                text_de=u'Nachricht auf de',
                text_fr=u'message en fr',
                start_ts=self.now,
                end_ts=self.now + timedelta(days=3),
                type=u'info'
            )
            session = create_session()
            session.add(sys_msg)
            session.flush()

        self.assertEqual(1, sys_msg.id)

        self.assertEqual(get_current_admin_unit(), sys_msg.admin_unit)
        self.assertEqual(get_current_admin_unit().unit_id, sys_msg.admin_unit_id)

        self.assertEqual(u'message in en', sys_msg.text_en)
        self.assertEqual(u'Nachricht auf de', sys_msg.text_de)
        self.assertEqual(u'message en fr', sys_msg.text_fr)

        self.assertEqual(self.now, sys_msg.start_ts)
        self.assertEqual(self.now + timedelta(days=3), sys_msg.end_ts)
        self.assertEqual(u'info', sys_msg.type)
