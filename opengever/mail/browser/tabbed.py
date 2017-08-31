from opengever.mail import _
from opengever.mail.interfaces import IMailTabbedviewSettings
from opengever.tabbedview import GeverTabbedView
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
