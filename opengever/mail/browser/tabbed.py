from opengever.mail import _
from opengever.tabbedview import GeverTabbedView


class MailTabbedView(GeverTabbedView):
    """Tabbedview for the ftw.mail.mail objects. Provides the following tabs:
    Overview, Preview, Journal, Sharing.
    """

    overview_tab = {
        'id': 'overview',
        'title': _(u'label_overview', default=u'Overview'),
        }

    preview_tab = {
        'id': 'preview',
        'title': _(u'label_preview', default=u'Preview'),
        }

    journal_tab = {
        'id': 'journal',
        'title': _(u'label_journal', default=u'Journal'),
        }

    sharing_tab = {
        'id': 'sharing',
        'title': _(u'label_sharing', default=u'Sharing'),
        }

    def _get_tabs(self):
        return [
            self.overview_tab,
            self.preview_tab,
            self.journal_tab,
            self.sharing_tab,
        ]
