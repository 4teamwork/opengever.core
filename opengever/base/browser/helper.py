from ftw.solr.interfaces import ISolrDocument
from opengever.globalindex.model.task import Task
from opengever.task.task import ITask
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.ZCatalog.interfaces import ICatalogBrain
from sqlalchemy.ext.declarative import DeclarativeMeta
from zope.component import getUtility


def _get_task_css_class(task):
    """A task helper function for `get_css_class`, providing some metadata
    of a task. The task may be a brain, a dexterity object or a sql alchemy
    globalindex object.
    """
    if ICatalogBrain.providedBy(task) or ISolrDocument.providedBy(task):
        task = Task.query.by_brain(task)

    if ITask.providedBy(task):
        task = task.get_sql_object()

    return task.get_css_class()


# XXX object orient me!
def get_css_class(item, type_icon_only=False):
    """Returns the content-type icon css class for `item`.

    Arguments:
    `item` -- obj or brain
    `type_icon_only` -- bool if it should only return the simple object
    type icon or the detailed content icon(mimetypes for document etc.).
    """
    css_class = None

    normalize = getUtility(IIDNormalizer).normalize
    if type_icon_only:
        return "contenttype-%s" % normalize(item.portal_type)

    if isinstance(type(item), DeclarativeMeta) or \
            item.portal_type == 'opengever.task.task':

        return _get_task_css_class(item)

    elif item.portal_type in ['opengever.document.document',
                              'opengever.meeting.sablontemplate',
                              'opengever.meeting.proposaltemplate']:

        # It's a document, we therefore want to display an icon
        # for the mime type of the contained file
        icon = getattr(item, 'getIcon', '')
        if callable(icon):
            icon = icon()

        if icon:
            # Strip '.gif' from end of icon name and remove
            # leading 'icon_'
            filetype = icon[:icon.rfind('.')].replace('icon_', '')
            css_class = 'icon-%s' % normalize(filetype)
        else:
            # Fallback for unknown file type
            css_class = "icon-document_empty"

        if getattr(item, '_v__is_relation', False):
            # Document was listed as a relation, so we use a special icon.
            css_class += " is-document-relation"
            # Immediatly set the volatile attribute to False so it doesn't
            # affect other views using the same object instance
            item._v__is_relation = False

    if css_class is None:
        css_class = "contenttype-%s" % normalize(item.portal_type)

    return css_class
