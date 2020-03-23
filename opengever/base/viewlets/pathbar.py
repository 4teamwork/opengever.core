from Acquisition import aq_chain
from opengever.base.browser.helper import get_css_class
from opengever.base.interfaces import ISQLObjectWrapper
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.service import ogds_service
from opengever.repository.interfaces import IRepositoryFolder
from opengever.repository.repositoryroot import IRepositoryRoot
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.viewlets import common
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PathBar(common.PathBarViewlet):
    """The breadcrumb viewlet.

    Unlike the plone default pathbar viewlet it groups all repository paths in
    to a dropdown list and shows the content icon for each crumb.
    """

    index = ViewPageTemplateFile('pathbar.pt')

    leaf_node = None
    repository_chain = None
    obj_chain = None

    def admin_unit_label(self):
        return get_current_admin_unit().label()

    def update(self):
        repository_items, self.obj_chain = self.get_chains()

        if repository_items:
            self.leaf_node = repository_items[0]
            if len(repository_items) > 1:
                self.repository_chain = repository_items[1:]

    def is_part_of_repo(self, obj):
        return IRepositoryRoot.providedBy(obj) or \
            IRepositoryFolder.providedBy(obj)

    def get_chains(self):
        repository = []
        chain = []
        for obj in aq_chain(self.context):
            if INavigationRoot.providedBy(obj):
                break

            if IHideFromBreadcrumbs.providedBy(obj):
                continue

            if ISQLObjectWrapper.providedBy(obj):
                data = obj.get_breadcrumb()
            else:
                data = {
                    'absolute_url': obj.absolute_url(),
                    'title': obj.Title(),
                    'css_class': get_css_class(obj, type_icon_only=True)
                }

            if self.is_part_of_repo(obj):
                repository.append(data)
            else:
                chain.append(data)

        chain.reverse()

        return repository, chain

    def has_multiple_admin_units(self):
        return ogds_service().has_multiple_admin_units()
