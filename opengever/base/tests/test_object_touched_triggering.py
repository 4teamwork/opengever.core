from opengever.base.touched import IObjectTouchedEvent
from opengever.testing import IntegrationTestCase
from opengever.testing.event_recorder import get_last_recorded_event
from opengever.testing.event_recorder import register_event_recorder
from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectModifiedEvent


class TestObjectTouchedTriggering(IntegrationTestCase):

    def test_gets_fired_on_object_modified(self):
        self.login(self.regular_user)

        register_event_recorder(IObjectTouchedEvent)
        notify(ObjectModifiedEvent(self.document))

        event = get_last_recorded_event()
        self.assertTrue(IObjectTouchedEvent.providedBy(event))

    def test_gets_fired_on_checkout(self):
        self.login(self.regular_user)

        register_event_recorder(IObjectTouchedEvent)
        self.checkout_document(self.document)

        event = get_last_recorded_event()
        self.assertTrue(IObjectTouchedEvent.providedBy(event))

    def test_gets_fired_on_checkin(self):
        self.login(self.regular_user)
        self.checkout_document(self.document)

        register_event_recorder(IObjectTouchedEvent)
        self.checkin_document(self.document)

        event = get_last_recorded_event()
        self.assertTrue(IObjectTouchedEvent.providedBy(event))

    def test_gets_fired_on_document_added(self):
        self.login(self.regular_user)

        register_event_recorder(IObjectTouchedEvent)
        notify(ObjectAddedEvent(self.document))

        event = get_last_recorded_event()
        self.assertTrue(IObjectTouchedEvent.providedBy(event))

    def test_gets_fired_on_mail_added(self):
        self.login(self.regular_user)

        register_event_recorder(IObjectTouchedEvent)
        notify(ObjectAddedEvent(self.mail))

        event = get_last_recorded_event()
        self.assertTrue(IObjectTouchedEvent.providedBy(event))
