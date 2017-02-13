from ftw.mail.interfaces import IEmailAddress
from opengever.base import _ as ogbmf
from opengever.base.viewlets.byline import BylineBase
from opengever.dossier import _
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.utils import get_main_dossier
from opengever.ogds.base.actor import Actor
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
import json


class BusinessCaseByline(BylineBase):
    """ Specific DocumentByLine, for the Businesscasedossier Type"""

    def start(self):
        dossier = IDossier(self.context)
        return self.to_localized_time(dossier.start)

    def responsible(self):
        responsible = Actor.user(IDossier(self.context).responsible)
        return responsible.get_link()

    def end(self):
        dossier = IDossier(self.context)
        return self.to_localized_time(dossier.end)

    note_template = ViewPageTemplateFile('templates/note.pt')

    def note(self):
        dossier = IDossier(self.context)
        msg_confirm = _(u'note_text_confirm_abord', default=u'Confirm abbord')
        msg_title_info = ogbmf(u'message_title_info', default=u'Information')
        msg_title_error = ogbmf(u'message_title_error', default=u'Error')
        msg_body_info = _(u'message_body_info', default=u'Changes saved')
        msg_body_error = _(u'message_body_error', default=u'Changes not saved')
        create_translations = lambda msg: translate(msg, context=self.request)

        translations = json.dumps(
            {'note_text_confirm_abord': create_translations(msg_confirm),
             'message_title_info': create_translations(msg_title_info),
             'message_title_error': create_translations(msg_title_error),
             'message_body_info': create_translations(msg_body_info),
             'message_body_error': create_translations(msg_body_error)
             })
        comments = '' if not dossier.comments else dossier.comments
        return self.note_template(note=comments,
                                  translations=translations)

    def mailto_link(self):
        """Displays email-address if the IMailInAddressMarker behavior
         is provided and the dossier is Active"""

        if self.get_current_state() in DOSSIER_STATES_OPEN:
            address = IEmailAddress(self.request
                                    ).get_email_for_object(self.context)
            return '<a href="mailto:%s">%s</a>' % (address, address)

    def get_items(self):
        items = [
            {
                'class': 'responsible',
                'label': _('label_responsible', default='Responsible'),
                'content': self.responsible(),
                'replace': True
            },
            {
                'class': 'review_state',
                'label': _('label_workflow_state', default='State'),
                'content': self.workflow_state(),
                'replace': False
            },
            {
                'class': 'start_date',
                'label': _('label_start_byline', default='from'),
                'content': self.start(),
                'replace': False
            },
            {
                'class': 'end_date',
                'label': _('label_end_byline', default='to'),
                'content': self.end(),
                'replace': False
            },
            {
                'class': 'sequenceNumber',
                'label': _('label_sequence_number', default='Sequence Number'),
                'content': self.sequence_number(),
                'replace': False
            },
            {
                'class': 'reference_number',
                'label': _('label_reference_number',
                           default='Reference Number'),
                'content': self.reference_number(),
                'replace': False
            },
            {
                'class': 'email',
                'label': _('label_email_address', default='E-Mail'),
                'content': self.mailto_link(),
                'replace': True
            }
        ]

        can_edit = api.user.has_permission('Modify portal content',
                                           obj=self.context)
        is_main_dossier = self.context == get_main_dossier(self.context)
        if is_main_dossier and can_edit:
            items += [
                {
                    'class': 'note',
                    'label': _('label_dossier_note', default='Dossiernote'),
                    'content': self.note(),
                    'replace': True
                }
            ]
        return items
