from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.contact import _
from opengever.contact import is_contact_feature_enabled
from opengever.kub import is_kub_feature_enabled
from Products.statusmessages.interfaces import IStatusMessage


class ContactFolderTabbedView(TabbedView):

    def __call__(self, *args, **kwargs):
        if is_kub_feature_enabled():
            msg = _(
                u'warning_kub_contact_new_ui_only',
                default=u'Kub contacts are only supported in the new frontend')
            IStatusMessage(self.request).addStatusMessage(msg, type=u'info')
        return super(ContactFolderTabbedView, self).__call__(*args, **kwargs)

    def get_tabs(self):
        if is_kub_feature_enabled():
            tabs = []
        elif is_contact_feature_enabled():
            tabs = [
                {'id': 'persons',
                 'title': _(u'label_persons', default=u'Persons'),
                 'icon': None,
                 'url': '#',
                 'class': None}]

        else:
            tabs = [
                {'id': 'local',
                 'title': _(u'label_local', default=u'Local'),
                 'icon': None,
                 'url': '#',
                 'class': None},
            ]

        tabs += [
            {'id': 'users',
             'title': _(u'label_users', default=u'Users'),
             'icon': None,
             'url': '#',
             'class': None},

            {'id': 'teams',
             'title': _(u'label_teams', default=u'Teams'),
             'icon': None,
             'url': '#',
             'class': None}]

        return tabs
