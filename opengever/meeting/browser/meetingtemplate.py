from opengever.base.browser.default_view import OGDefaultView
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import json


class MeetingTemplateView(OGDefaultView):

    template = ViewPageTemplateFile('templates/meetingtemplate.pt')

    def paragraphs(self):
        return self.context.get_paragraphs()

    @property
    def url_update_order(self):
        return '{}/@@update_content_order'.format(self.context.absolute_url())


class UpdateMeetingTemplateContentOrderView(BrowserView):

    def __call__(self):
        order = reversed(json.loads(self.request.get('sortOrder')))

        for object_id in order:
            self.context.moveObjectsToTop([object_id])

        return self.request.RESPONSE.redirect(self.context.absolute_url())
