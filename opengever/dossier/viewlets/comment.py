from opengever.base import _ as ogbmf
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.utils import get_main_dossier
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
import json


class BusinessCaseCommentViewlet(ViewletBase):

    index = ViewPageTemplateFile('templates/note.pt')

    def available(self):
        return self.context == get_main_dossier(self.context)

    def translations(self):
        msg_confirm = _(u'note_text_confirm_abord', default=u'Confirm abbord')
        msg_title_info = ogbmf(u'message_title_info', default=u'Information')
        msg_title_error = ogbmf(u'message_title_error', default=u'Error')
        msg_body_info = _(u'message_body_info', default=u'Changes saved')
        msg_body_error = _(u'message_body_error', default=u'Changes not saved')
        create_translations = lambda msg: translate(msg, context=self.request)

        return json.dumps(
            {'note_text_confirm_abord': create_translations(msg_confirm),
             'message_title_info': create_translations(msg_title_info),
             'message_title_error': create_translations(msg_title_error),
             'message_body_info': create_translations(msg_body_info),
             'message_body_error': create_translations(msg_body_error)
             })

    def note(self):
        dossier = IDossier(self.context)
        return '' if not dossier.comments else dossier.comments
