from opengever.base.browser.default_view import OGDefaultView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class MeetingTemplateView(OGDefaultView):

    template = ViewPageTemplateFile('templates/meetingtemplate.pt')

    def paragraphs(self):
        return self.context.get_paragraphs()

    @property
    def url_update_order(self):
        return ''
