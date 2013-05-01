"""
This module contains the tabbed views and all the stuff used in the OGDS
control panel.
"""

from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from five import grok
from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.globalindex import Session
from opengever.globalindex.model.task import Task
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingTab


class OGDSControlPanel(grok.View, TabbedView):
    """Control panel tabbed view.
    """

    grok.context(IPloneSiteRoot)
    grok.name('ogds-controlpanel')
    grok.require('cmf.ManagePortal')

    tabs = [
        {'id': 'ogds-cp-clients',
         'icon': None,
         'url': '#',
         'class': None},

        {'id': 'users',
         'icon': None,
         'url': '#',
         'class': None},

        {'id': 'ogds-cp-alltasks',
         'icon': None,
         'url': '#',
         'class': None},
        ]

    def __init__(self, *args, **kwargs):
        grok.View.__init__(self, *args, **kwargs)
        TabbedView.__init__(self, *args, **kwargs)

    def get_tabs(self):
        return self.tabs

    def render(self):
        return TabbedView.__call__(self)


class OGDSAllTasks(GlobalTaskListingTab):
    """Lists all tasks in the globalindex.
    """

    grok.context(IPloneSiteRoot)
    grok.name('tabbedview_view-ogds-cp-alltasks')
    grok.require('cmf.ManagePortal')

    enabled_actions = major_actions = ['pdf_taskslisting']

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """

        return Session().query(Task)
