from DateTime import DateTime
from logging import getLogger
from opengever.base.helpers import display_name
from os import environ
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
import requests


logger = getLogger('opengever.workspace')


class MeetingMinutesPDFView(BrowserView):

    template = ViewPageTemplateFile("templates/meeting_minutes.pt")

    def __call__(self):
        weasyprint_url = environ.get('WEASYPRINT_URL')
        if not weasyprint_url:
            logger.error('Weasyprint url not configured.')
            self.request.response.setStatus(500)
            return 'PDF generation failed.'

        resp = None
        try:
            resp = requests.post(
                weasyprint_url, files={'html': self.meeting_minutes_html()})
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            details = resp.content[:200] if resp is not None else ''
            logger.exception('PDF generation failed. %s', details)
            self.request.response.setStatus(500)
            return 'PDF generation failed.'
        else:
            self.request.response.setHeader('Content-Type', 'application/pdf')
            return resp.content

    def meeting_minutes_html(self):
        data = {}
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        data['generator'] = portal_state.portal_title()
        data['print_date'] = DateTime()
        data['responsible'] = display_name(self.context.responsible)

        data['agenda_items'] = []
        agenda_items = self.context.getFolderContents(
            {'portal_type': 'opengever.workspace.meetingagendaitem'})
        for i, item in enumerate(agenda_items):
            obj = item.getObject()
            text = obj.text.output if obj.text else ''
            decision = obj.decision.output if obj.decision else ''
            data['agenda_items'].append({
                'number': '{}. '.format(i + 1),
                'title': obj.Title(),
                'text': text,
                'decision': decision,
            })

        return self.template(self, **data)
