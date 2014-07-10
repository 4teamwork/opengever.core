from opengever.base.browser.helper import get_css_class
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.dexterity.interfaces import IDexterityContent
from plone.formwidget.contenttree.interfaces import IContentTreeWidget
from plone.formwidget.contenttree.navtree import NavtreeStrategy
from zope.component import adapts
from zope.interface import implements


class OpengeverNavtreeStrategy(NavtreeStrategy):
    """The navtree strategy used for the contenttree widget in OpenGever.

    We use this to override the `normalized_portal_type` attribute for
    document nodes. This allow us to include the sprite mimetype icons
    for all documents. (See plone.formwidget.contenttree.input_recurse.pt)

    Because the `normalized_portal_type` attribute is only used by the
    contenttree widgets, it's save to overwrite this attribute.
    """

    implements(INavtreeStrategy)
    adapts(IDexterityContent, IContentTreeWidget)

    def decoratorFactory(self, node):
        new_node = super(OpengeverNavtreeStrategy, self).decoratorFactory(node)
        if new_node.get('portal_type', '') == 'opengever.document.document':
            brain = new_node.get('item_icon').brain
            new_node['normalized_portal_type'] = ' {}'.format(
                get_css_class(brain))

            new_node['item_icon'] = None

        return new_node
