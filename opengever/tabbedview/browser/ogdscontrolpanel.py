"""
This module contains the tabbed views and all the stuff used in the OGDS
control panel.
"""

from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.globalindex.model.task import Task
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingTab


class OGDSControlPanel(TabbedView):
    """Control panel tabbed view.
    """

    tabs = [
        {'id': 'users',
         'icon': None,
         'url': '#',
         'class': None},

        {'id': 'ogds-cp-alltasks',
         'icon': None,
         'url': '#',
         'class': None},
    ]

    def get_tabs(self):
        return self.tabs

    def render(self):
        return TabbedView.__call__(self)


class OGDSAllTasks(GlobalTaskListingTab):
    """Lists all tasks in the globalindex.
    """

    enabled_actions = major_actions = ['pdf_taskslisting']

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """
        return Task.query
