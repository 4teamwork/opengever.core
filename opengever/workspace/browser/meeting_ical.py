from icalendar import Calendar
from icalendar import Event
from icalendar import vCalAddress
from icalendar import vText
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.ogds.models.service import ogds_service
from Products.Five.browser import BrowserView


class MeetingICalExportView(BrowserView):
    """ICal Export view called by the meeting_ical_download action."""

    def __call__(self):
        cal = Calendar()
        event = Event()

        event.add('summary', self.context.title)
        event.add('dtstart', self.context.start)
        if self.context.end:
            event.add('dtend', self.context.end)

        event.add('dtstamp', self.context.created().asdatetime())

        self.add_organizer(event)
        self.add_location(event)
        self.add_attendees(event)

        cal.add_component(event)

        response = self.request.RESPONSE
        response.setHeader('Content-Type', 'text/calendar')
        set_attachment_content_disposition(
            self.request, u'{}.ics'.format(self.context.getId()))

        return cal.to_ical()

    def add_organizer(self, event):
        if not self.context.responsible:
            return

        user = ogds_service().fetch_user(self.context.responsible)
        organizer = vCalAddress('MAILTO:{}'.format(user.email))
        organizer.params['cn'] = vText(user.fullname())
        event['organizer'] = organizer

    def add_location(self, event):
        if self.context.location:
            event['location'] = vText(self.context.location)

    def add_attendees(self, event):
        for attendee in self.context.attendees:
            user = ogds_service().fetch_user(attendee)
            attendee = vCalAddress('MAILTO:{}'.format(user.email))
            attendee.params['cn'] = vText(user.fullname())
            attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
            event.add('attendee', attendee, encode=0)
