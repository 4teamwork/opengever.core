from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from opengever.repository.interfaces import IRepositoryFolder
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import isDefaultPage
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, IOpengeverBaseLayer)
class Breadcrumbs(object):
    """
    Generates a list of dicts containing all ancestors of the context.

    In contrast to `plone.restapi` which makes use of
    `Products.CMFPlone.browser.navigation.PhysicalNavigationBreadcrumbs` we
    build the breadcrumbs by ourselves because we need to return additional data
    of the breadcrumbs.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "breadcrumbs": {
                "@id": "{}/@breadcrumbs".format(self.context.absolute_url())
            }
        }
        if not expand:
            return result
        result["breadcrumbs"]["items"] = self.get_serialized_breadcrumbs()
        return result

    def get_serialized_breadcrumbs(self):
        items = []
        obj = self.context
        while obj and not IPloneSiteRoot.providedBy(obj):
            if self.is_visible_breadcrumb(obj):
                item = getMultiAdapter((obj, self.request), ISerializeToJsonSummary)()

                item['is_leafnode'] = None
                if IRepositoryFolder.providedBy(obj):
                    item['is_leafnode'] = obj.is_leaf_node()

                if IDossierMarker.providedBy(obj) or IDossierTemplateMarker.providedBy(obj):
                    item['is_subdossier'] = obj.is_subdossier()

                items.append(item)
            obj = aq_parent(aq_inner(obj))
        items.reverse()
        return items

    def is_visible_breadcrumb(self, obj):
        """
        Just like `Products.CMFPlone.browser.navigation.PhysicalNavigationBreadcrumbs`
        we do not consider every content object to be a breadcrumb.
        """
        return not(IHideFromBreadcrumbs.providedBy(obj) or isDefaultPage(obj, self.request))


class BreadcrumbsGet(Service):
    def reply(self):
        breadcrumbs = Breadcrumbs(self.context, self.request)
        return breadcrumbs(expand=True)["breadcrumbs"]
