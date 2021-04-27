from opengever.meeting.reopen import ReopenMeeting
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form.form import Form


class ReopenMeetingForm(Form):
    ignoreContext = True

    def prepare_reopener(self):
        self.reopener = ReopenMeeting(self.context.model)
        self.errors = self.reopener.get_errors()

    def render(self):
        self.request.set('disable_border', True)
        self.prepare_reopener()
        return self.index()

    @button.buttonAndHandler(u'Confirm')
    def handle_confirm(self, action):
        self.prepare_reopener()
        data, errors = self.extractData()
        if not errors:
            reopen_errors = self.reopener.get_errors()
            status = IStatusMessage(self.request)
            if reopen_errors:
                for msg in reopen_errors:
                    status.addStatusMessage(msg, type='error')
            else:
                self.reopener.reopen_meeting()
                msg = u'The meeting has been reopened.'
                status.addStatusMessage(msg, type='info')

            return self._redirect_to_meeting()

    @button.buttonAndHandler(u'Cancel')
    def handle_cancel(self, action):
        return self._redirect_to_meeting()

    def _redirect_to_meeting(self):
        url = self.context.model.get_url()
        return self.request.RESPONSE.redirect(url)
