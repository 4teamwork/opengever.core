from ftw.mail.interfaces import IEmailAddress
from opengever.base.viewlets.byline import BylineBase
from opengever.dossier import _
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.resolve import AfterResolveJobs
from opengever.dossier.resolve_lock import ResolveLock
from opengever.ogds.base.actor import Actor
from plone import api
from zope.globalrequest import getRequest
from zope.i18n import translate


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

    def is_resolve_locked(self):
        return ResolveLock(self.context).is_locked(recursive=False)

    def after_resolve_jobs_pending(self):
        return AfterResolveJobs(self.context).after_resolve_jobs_pending

    def mailto_link(self):
        """Displays email-address if the IMailInAddressMarker behavior
         is provided and the dossier is Active"""

        if self.get_current_state() in DOSSIER_STATES_OPEN:
            address = IEmailAddress(self.request
                                    ).get_email_for_object(self.context)
            return '<a href="mailto:%s">%s</a>' % (address, address)

    def external_reference(self):
        return IDossier(self.context).external_reference

    def external_reference_link(self):
        if not self.external_reference():
            return self.external_reference()
        ref_tag = api.portal.get_tool(name='portal_transforms').convertTo(
            'text/html', self.external_reference(),
            mimetype='text/x-web-intelligent').getData()
        return '<span>%s</span>' % ref_tag

    def workflow_state(self):
        """If the dossier is currently being resolved, extend translated
        workflow state with a message saying so.
        """
        wfstate = super(BusinessCaseByline, self).workflow_state()
        if self.is_resolve_locked():
            wfstate = translate(wfstate, context=getRequest())
            wfstate += translate(_(u' (currently being resolved)'), context=getRequest())

        # Add a debug hint for Managers if a dossier's nightly
        # AfterResolveJobs haven't been executed yet.
        is_manager = api.user.get_current().has_role('Manager')
        if is_manager and self.after_resolve_jobs_pending():
            wfstate = translate(wfstate, context=getRequest())
            wfstate += translate(_(u' (after resolve jobs pending)'), context=getRequest())

        return wfstate

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
            },
            {
                'class': 'external_reference',
                'label': _('label_external_reference',
                           default=u'External Reference'),
                'content': self.external_reference_link(),
                'replace': True
            }
        ]

        return items
