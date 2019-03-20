from opengever.mail import _
from opengever.mail.interfaces import IMailTabbedviewSettings
from opengever.tabbedview import GeverTabbedView
from opengever.trash.trash import ITrashed
from plone import api


class MailTabbedView(GeverTabbedView):
    """Tabbedview for the ftw.mail.mail objects. Provides the following tabs:
    Overview, Preview (configurable), Journal, Sharing.
    """

    overview_tab = {
        'id': 'overview',
        'title': _(u'label_overview', default=u'Overview'),
        }

    journal_tab = {
        'id': 'journal',
        'title': _(u'label_journal', default=u'Journal'),
        }

    sharing_tab = {
        'id': 'sharing',
        'title': _(u'label_sharing', default=u'Sharing'),
        }

    def __init__(self, context, request):
        """Slap a warning onto the overview of a trashed mail.

        We're asserting on the request not having a form as the tabs themselves,
        which get requested by AJAX, rely on a form in the request data. If
        we'd also slap the portal warning onto those requests, the next 'full'
        page view would display them, as the tabs do not consume a portal
        warning.
        """
        super(MailTabbedView, self).__init__(context, request)
        if ITrashed.providedBy(self.context):
            if not self.request.form:
                msg = _(u'warning_trashed', default=u'This mail is trashed.')
                api.portal.show_message(msg, self.request, type='warning')

    @property
    def preview_tab(self):
        if api.portal.get_registry_record(
                name='preview_tab_visible', interface=IMailTabbedviewSettings):
            return {
                'id': 'preview',
                'title': _(u'label_preview', default=u'Preview'),
            }

        return None

    def _get_tabs(self):
        return filter(None, [
            self.overview_tab,
            self.preview_tab,
            self.journal_tab,
            self.sharing_tab,
        ])
