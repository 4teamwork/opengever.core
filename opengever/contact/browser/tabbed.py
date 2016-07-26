from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.contact import _
from opengever.contact import is_contact_feature_enabled


class ContactFolderTabbedView(TabbedView):

    def get_tabs(self):
        tabs = [
            {'id': 'local',
             'title': _(u'label_local', default=u'Local'),
             'icon': None,
             'url': '#',
             'class': None},
            {'id': 'users',
             'title': _(u'label_users', default=u'Users'),
             'icon': None,
             'url': '#',
             'class': None},
        ]

        if is_contact_feature_enabled():
            tabs += [
                {'id': 'persons',
                 'title': _(u'label_persons', default=u'Persons'),
                 'icon': None,
                 'url': '#',
                 'class': None},
                {'id': 'organizations',
                 'title': _(u'label_organizations', default=u'Organizations'),
                 'icon': None,
                 'url': '#',
                 'class': None}]

        return tabs
