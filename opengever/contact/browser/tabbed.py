from ftw.tabbedview.browser.tabbed import TabbedView


class ContactFolderTabbedView(TabbedView):

    def get_tabs(self):
        return [
            {'id': 'local', 'icon': None, 'url': '#', 'class': None},
            {'id': 'users', 'icon': None, 'url': '#', 'class': None},
        ]
