from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.dexterity.interfaces import IDexterityContent
from plone.formwidget.contenttree.interfaces import IContentTreeWidget
from plone.formwidget.contenttree.navtree import NavtreeStrategy
from plone.memoize.instance import memoize
from zope.component import adapts
from zope.interface import implements


class FakeCatalogBrainContentIcon(object):
    """A fake CatalogBrainContentIcon.

    This is needed because on the original CatalogBrainContentIcon `url` is a
    read only property, therefore we can't override it in the decoratorFactory
    of our custom navtree strategy for the ContentTreeWidget.
    """

    def __init__(self):
        self.url = ''
        self.width = 16
        self.height = 16
        self.title = None
        self.description = ""

    @memoize
    def html_tag(self):

        if not self.url:
            return None

        tag = '<img width="%s" height="%s" src="%s"' % (
            self.width, self.height, self.url,)

        if self.title:
            tag += ' title="%s"' % self.title
        if self.description:
            tag += ' alt="%s"' % self.description
        tag += ' />'
        return tag


class OpengeverNavtreeStrategy(NavtreeStrategy):
    """The navtree strategy used for the content tree widget in OpenGever.

    We use this to override the item_icon's url for documents without a file,
    so the generic document icon is displayed even if no mimetype can be
    determined.
    """

    implements(INavtreeStrategy)
    adapts(IDexterityContent, IContentTreeWidget)

    def decoratorFactory(self, node):
        new_node = super(OpengeverNavtreeStrategy, self).decoratorFactory(node)
        if new_node.get('portal_type', '') == 'opengever.document.document':
            doc = new_node['item'].getObject()
            if not doc.file:
                # If document doesn't have a file, and therefore the
                # mimetype can't be determined, override the icon
                # with the generic document icon
                new_icon = FakeCatalogBrainContentIcon()
                new_icon.url = 'document_icon.gif'
                new_node['item_icon'] = new_icon
        return new_node
