from opengever.base.browser.default_view import OGDefaultView
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import NotFound


class MeetingTemplateView(OGDefaultView):

    template = ViewPageTemplateFile('templates/meetingtemplate.pt')

    def paragraphs(self):
        return self.context.get_paragraphs()

    @property
    def url_update_order(self):
        return '{}/update_order'.format(self.context.absolute_url())


class UpdateMeetingTemplateParagraphOrderView(OGDefaultView):

    def __call__(self):
        meeting_template = self.get_meeting_template()

        assert False, 'WIP'

        return self.request.RESPONSE.redirect(meeting_template.get_url())

    def get_meeting_template(self):
        meeting_template_id = self.request.get('meeting-template-id')
        if not meeting_template_id:
            raise NotFound

        templates = api.content.find(
            id=meeting_template_id,
            portal_type='opengever.meeting.meetingtemplate')

        if len(templates) == 0:
            raise NotFound

        assert 1 == len(templates), 'Only one meeting template expected'

        return templates[0]
