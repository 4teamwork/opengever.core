from plone.app.uuid.utils import uuidToObject
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter


def _breadcrumbs_from_obj(obj):
    """Returns a list of titles for the items parent hierarchy (breadcrumbs).
    """
    breadcrumb_titles = []
    breadcrumbs_view = getMultiAdapter((obj, obj.REQUEST),
                                       name='breadcrumbs_view')
    raw_breadcrumb_titles = breadcrumbs_view.breadcrumbs()

    # Make sure all titles are utf-8
    for elem in raw_breadcrumb_titles:
        title = elem.get('Title')
        if isinstance(title, unicode):
            title = title.encode('utf-8')
        breadcrumb_titles.append(title)
    # Make sure all data used in the HTML snippet is properly escaped
    return " > ".join(t for t in breadcrumb_titles)


class ResolveUidToBreadcrumb(BrowserView):

    def __call__(self):
        uid = self.request.get('ploneuid', None)

        if uid is None:
            raise AttributeError('Missing a plone uid')

        return _breadcrumbs_from_obj(uuidToObject(uid))
