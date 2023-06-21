from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import datetime
from logging import getLogger
from opengever.base.helpers import display_name
from opengever.base.interfaces import IWhiteLabelingSettings
from opengever.dossier.utils import get_main_dossier
from opengever.workspace.interfaces import IWorkspaceMeetingAttendeesPresenceStateStorage
from opengever.workspace.workspace_meeting import ALLOWED_ATTENDEES_PRESENCE_STATES
from os import environ
from plone import api
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.i18n import translate
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

        files = {'html': self.meeting_minutes_html()}
        customer_logo = self.get_customer_logo_src()
        if customer_logo:
            files['asset.customer_logo'] = customer_logo

        workspace = get_main_dossier(self.context)
        if workspace.workspace_logo:
            files['asset.workspace_logo'] = workspace.workspace_logo.data

        try:
            resp = requests.post(weasyprint_url, files=files)

            resp.raise_for_status()
        except requests.exceptions.RequestException:
            details = resp.content[:200] if resp is not None else ''
            logger.exception('PDF generation failed. %s', details)
            self.request.response.setStatus(500)
            return 'PDF generation failed.'
        else:
            self.request.response.setHeader('Content-Type', 'application/pdf')
            return resp.content

    def prepare_header_and_footer(self):
        header = self.context.meeting_template_header or {}
        footer = self.context.meeting_template_footer or {}

        return self._format_strings(header), self._format_strings(footer)

    def get_customer_logo_src(self):
        return api.portal.get_registry_record(
            'logo_src', interface=IWhiteLabelingSettings)

    def _format_strings(self, data):
        dynamic_information = {
            'page_number': '"counter(page)"',
            'number_of_pages': '"counter(pages)"',
            'print_date': self.context.toLocalizedTime(datetime.now()),
            'customer_logo': '"url(\"asset.customer_logo\")"',
            'workspace_logo': '"url(\"asset.workspace_logo\")"',
        }

        return {key: '"{}"'.format(data.get(key, '').format(**dynamic_information))
                for key in ['left', 'center', 'right']}

    def meeting_minutes_html(self):
        data = {}
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        data['generator'] = portal_state.portal_title()
        data['responsible'] = display_name(self.context.responsible)
        data['chair'] = display_name(self.context.chair)
        data['secretary'] = display_name(self.context.secretary)
        data['attendees'] = []
        presence_states = IWorkspaceMeetingAttendeesPresenceStateStorage(self.context).get_all()
        for attendee in self.context.attendees:
            state = translate(ALLOWED_ATTENDEES_PRESENCE_STATES[presence_states[attendee]],
                              context=self.request)
            data['attendees'].append(u'{} ({})'.format(display_name(attendee), safe_unicode(state)))
        data['agenda_items'] = []
        agenda_items = self.context.getFolderContents(
            {'portal_type': 'opengever.workspace.meetingagendaitem'})
        for i, item in enumerate(agenda_items):
            obj = item.getObject()
            text = obj.text.output if obj.text else ''
            decision = obj.decision.output if obj.decision else ''
            related_items = [item.to_object for item in obj.relatedItems if item.to_object]
            data['agenda_items'].append({
                'number': '{}. '.format(i + 1),
                'title': obj.Title(),
                'text': text,
                'decision': decision,
                'related_items': [
                    {'title': item.Title(), 'url': item.absolute_url()}
                    for item in related_items]
            })

        data['header'], data['footer'] = self.prepare_header_and_footer()

        return self.template(self, **data)
