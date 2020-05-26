from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.formwidget.contenttree.utils import closest_content
from plone.formwidget.contenttree.widget import Fetch
from Products.CMFCore.utils import getToolByName
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
import urllib


# Customization of p.formwidget.contenttree:
# Does the same as the original but only returns a maximum of 100 children and
# supports a b_start parameter for fetching further batches.
class Fetch(Fetch):

    fragment_template = ViewPageTemplateFile('templates/fragment.pt')

    def __call__(self):
        # We want to check that the user was indeed allowed to access the
        # form for this widget. We can only this now, since security isn't
        # applied yet during traversal.
        self.validate_access()

        widget = self.context
        context = widget.context

        # Update the widget before accessing the source.
        # The source was only bound without security applied
        # during traversal before.
        widget.update()
        source = widget.bound_source

        # Convert token from request to the path to the object
        token = self.request.form.get('href', None)
        if token is not None:
            token = urllib.unquote(token)
        directory = self.context.bound_source.tokenToPath(token)
        level = self.request.form.get('rel', 0)

        b_start = self.request.form.get('b_start', 0)
        try:
            b_start = int(b_start)
        except ValueError:
            b_start = 0
        b_size = 100

        navtree_query = source.navigation_tree_query.copy()

        if widget.show_all_content_types and 'portal_type' in navtree_query:
            del navtree_query['portal_type']

        if directory is not None:
            navtree_query['path'] = {'depth': 1, 'query': directory}

        if 'is_default_page' not in navtree_query:
            navtree_query['is_default_page'] = False

        content = closest_content(context)

        strategy = getMultiAdapter((content, widget), INavtreeStrategy)
        catalog = getToolByName(content, 'portal_catalog')

        results = catalog(navtree_query)
        if len(results) > b_start + b_size + 1:
            has_more = True
        else:
            has_more = False

        children = []
        for brain in results[b_start:b_start + b_size]:
            newNode = {'item': brain,
                       'depth': -1,  # not needed here
                       'currentItem': False,
                       'currentParent': False,
                       'children': []}
            if strategy.nodeFilter(newNode):
                newNode = strategy.decoratorFactory(newNode)
                children.append(newNode)

        self.request.response.setHeader('X-Theme-Disabled', 'True')

        return self.fragment_template(
            children=children, level=int(level), b_start=b_start + b_size,
            has_more=has_more,
        )
