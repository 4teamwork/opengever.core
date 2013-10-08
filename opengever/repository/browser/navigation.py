from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from opengever.base.browser.navtree import OpengeverNavtreeStrategy
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.portlets.portlets.navigation import INavigationPortlet
from Products.CMFPlone.browser.navtree import DefaultNavtreeStrategy
from plone.formwidget.contenttree.interfaces import IContentTreeWidget
from zope.component import adapts
from zope.interface import implements, Interface
from opengever.repository.utils import getAlternativeLanguageCode


class NavtreeStrategy(DefaultNavtreeStrategy):
    implements(INavtreeStrategy)
    adapts(Interface, INavigationPortlet)

    def __init__(self, context, view=None):
        super(NavtreeStrategy, self).__init__(context, view)

    def decoratorFactory(self, node):
        nodes = super(NavtreeStrategy, self).decoratorFactory(node)
        nodes['Title'] = self.get_title_of(nodes.get('item'))
        return nodes

    def get_title_of(self, item):
        lang_code = self.get_preferred_language_code()

        if (lang_code == getAlternativeLanguageCode() and
             getattr(item, 'alternative_title', None)):
            return getattr(item, 'alternative_title')

        else:
            context = aq_inner(self.context)
            return utils.pretty_title_or_id(context, item)

    def get_preferred_language_code(self):
        ltool = getToolByName(self.context, 'portal_languages')
        if len(ltool.getPreferredLanguage().split('-')) > 1:
            return ltool.getPreferredLanguage().split('-')[0]
        return ltool.getPreferredLanguage()


class ContentTreeNavtreeStrategy(OpengeverNavtreeStrategy):
    implements(INavtreeStrategy)
    adapts(Interface, IContentTreeWidget)

    def decoratorFactory(self, node):
        nodes = super(
            ContentTreeNavtreeStrategy, self).decoratorFactory(node)
        nodes['Title'] = self.get_title_of(nodes.get('item'))
        return nodes

    def get_title_of(self, item):
        lang_code = self.get_preferred_language_code()

        if (lang_code == getAlternativeLanguageCode() and
             getattr(item, 'alternative_title', None)):
                return getattr(item, 'alternative_title')

        else:
            context = aq_inner(self.context)
            return utils.pretty_title_or_id(context, item)

    def get_preferred_language_code(self):
        ltool = getToolByName(self.context, 'portal_languages')
        if len(ltool.getPreferredLanguage().split('-')) > 1:
            return ltool.getPreferredLanguage().split('-')[0]
        return ltool.getPreferredLanguage()
