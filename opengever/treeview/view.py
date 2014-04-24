from Products.CMFPlone.browser.navigation import CatalogNavigationTree
from Products.CMFPlone.utils import getToolByName
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from navtree import  buildFolderTree
# TODO: implements the treeportlet persistent
# import simplejson as json
# from ftw.dictstorage.interfaces import IDictStorage

class TreeView(CatalogNavigationTree):

    recurse = ViewPageTemplateFile('recurse.pt')

    def render(self, root_path=None):
        """return a html tree for treeview
        """
        if root_path:
            portal_url = getToolByName(self.context, 'portal_url')
            current = portal_url.getPortalObject().restrictedTraverse(
                root_path.encode('utf-8'))
            #check if the actual context is in the current repositoryroot
            if root_path in self.context.getPhysicalPath():
                context = aq_inner(self.context)
                return self.get_tree(context, current)
            else:
                return self.get_tree(current, current)
        else:
            current = context = aq_inner(self.context)
            return self.get_tree(context, current)

    def get_tree(self, context, current):
        self.context = context
        # Don't travsere to top-level application obj if TreePortlet
        # was added to the Plone Site Root
        if current.Type() == 'Plone Site':
            return current.Title()
        else:
            while current.Type() != 'RepositoryRoot' \
              and current.Type() != 'Plone Site':
                current = current.aq_parent

        query = {
            'path': dict(query='/'.join(current.getPhysicalPath()), depth=-1),
            'Type': 'RepositoryFolder'}
        strategy = getMultiAdapter((context.aq_inner, self), INavtreeStrategy)

        # # we access configuration in as json under some key
        # configuration = IDictStorage(self)
        # custom = json.loads(configuration.get(
        #     # make sure key is unique as "deep" as you want
        #     'ftw-treeview-opengever-mandat1-username',
        #     # return default settings
        #     '{}'))
        # # now use the to create html
        # raise NotImplemented

        data = buildFolderTree(context.aq_inner,
            obj=context.aq_inner, query=query, strategy=strategy)
        if data.get('children'):
            children = data.get('children')[0].get('children')
            html=self.recurse(children=children, level=1, bottomLevel=999,
                              language=self.get_preferred_language_code())
            return html
        else:
            return ''

    def get_preferred_language_code(self):
        ltool = getToolByName(self.context, 'portal_languages')
        return ltool.getPreferredLanguage()
