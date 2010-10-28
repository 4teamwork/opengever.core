from zope.interface import implements
from zope.component import adapts
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.formwidget.contenttree.navtree import NavtreeStrategy
from plone.formwidget.contenttree.interfaces  import IContentTreeWidget
from OFS.interfaces import IItem

class OpengeverNavtreeStrategy(NavtreeStrategy):
    """Override the navtree strategy fro plone.formwidget.contenttree
    it set showChildrenOf to false
    """
    implements(INavtreeStrategy)
    adapts(IItem, IContentTreeWidget)
    
    def showChildrenOf(self, object):
        # Allow entering children even if the type would not normally be
        # expanded in the navigation tree
        return False
