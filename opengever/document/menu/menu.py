from Acquisition import aq_inner
from plone import api
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from zope.app.component.hooks import getSite
from zope.app.publisher.browser.menu import BrowserMenu
from zope.app.publisher.browser.menu import BrowserSubMenuItem
from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.publisher.interfaces.browser import IBrowserSubMenuItem
from zope.component import getMultiAdapter
from zope.interface import implements


class ICheckinMenu(IBrowserMenu):
    """The checkin menu.
    """


class ICheckinMenuItem(IBrowserSubMenuItem):
    """The menu item linking to the checkin menu.
    """


class CheckinMenu(BrowserMenu):
    implements(IBrowserMenu)

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""

        actions_tool = api.portal.get_tool('portal_actions')
        edit_actions = actions_tool.listActionInfos(
            object=aq_inner(context), categories=('object_checkin_menu',))

        if not edit_actions:
            return []

        results = []
        plone_utils = api.portal.get_tool('plone_utils')
        portal_url = api.portal.get().absolute_url()

        for action in edit_actions:
            if action['allowed']:
                cssClass = 'actionicon-object_checkin_menu-%s' % action['id']
                icon = plone_utils.getIconFor('object_checkin_menu',
                                              action['id'], None)
                if icon:
                    icon = '%s/%s' % (portal_url, icon)

                results.append({
                    'title': action['title'],
                    'description': '',
                    'action': action['url'],
                    'selected': False,
                    'icon': icon,
                    'extra': {
                        'id': action['id'],
                        'separator': None,
                        'class': cssClass},
                    'submenu': None})

        return results


class CheckinSubMenuItem(BrowserSubMenuItem):
    implements(ICheckinMenuItem)

    title = 'Checkin'
    description = ''
    submenuId = 'checkin_contentmenu'

    order = 10
    extra = {'id': 'plone-contentmenu-checkin'}

    def __init__(self, context, request):
        BrowserSubMenuItem.__init__(self, context, request)
        self.context_state = getMultiAdapter((context, request),
                                             name='plone_context_state')

    @property
    def action(self):
        folder = self.context
        if not self.context_state.is_structural_folder():
            folder = utils.parent(self.context)
        return folder.absolute_url() + '/folder_contents'

    @memoize
    def available(self):
        actions_tool = api.portal.get_tool('portal_actions')
        edit_actions = actions_tool.listActionInfos(
            object=aq_inner(self.context),
            categories=('object_checkin_menu', ),
            max=1)
        return len(edit_actions) > 0

    def selected(self):
        return False
