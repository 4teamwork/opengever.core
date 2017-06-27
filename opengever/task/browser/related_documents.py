from five import grok
from ftw.table.catalog_source import default_custom_sort
from ftw.table.interfaces import ICatalogTableSourceConfig
from ftw.table.interfaces import ITableSource
from opengever.tabbedview import GeverCatalogTableSource
from opengever.tabbedview.browser.tabs import BaseTabProxy
from opengever.tabbedview.browser.tabs import Documents
from opengever.task.task import ITask
from operator import attrgetter
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import sortable_title
from zope.interface import Interface


class BrainWrapper(object):
    """ Used to provide the _v__is_related attr on a brain
    """

    def __init__(self, brain):
        self.brain = brain

    def __getattr__(self, attr):
        if attr == '_v__is_relation':
            return True
        return getattr(self.brain, attr)


def sortable_title_transform(brain, value):
    """This transform should only be used for sorting items by title
    using the sortable_title indexer. Its used as wrapper for for the
    CatalogTool sortable_title indexer for making it callable like a
    normal ftw.table transform.
    """

    return sortable_title(brain)()


class IRelatedDocumentsCatalogTableSourceConfig(ICatalogTableSourceConfig):
    """Related documents table source config interface
    """


class RelatedDocumentsCatalogTableSource(GeverCatalogTableSource):
    """Related documents table source adapter
    """

    grok.implements(ITableSource)
    grok.adapts(IRelatedDocumentsCatalogTableSourceConfig, Interface)

    def build_query(self):
        """Builds the query based on `get_base_query()` method of config.
        Returns the query object.

        We need all documents listed in folder_contents and the related
        documents on the task. So we need to get all brains before we start
        to sort and filtering
        """

        # initalize config
        self.config.update_config()

        # get the base query from the config
        query = self.config.get_base_query()

        brains = []

        brains += self.get_containing_documents(query)
        brains += self.get_related_documents()

        # ordering
        brains = self.extend_query_with_ordering(brains)

        # filter
        brains = self.extend_query_with_textfilter(
            brains,
            self.config.filter_text,
            )

        return brains

    def get_related_documents(self):
        """ Return the related documents from a task
        We get objects but we need brains. So we lookup them
        """
        brains = []
        for item in self.config.context.relatedItems:
            obj = item.to_object

            if obj.portal_type in [
                'opengever.document.document', 'ftw.mail.mail']:

                brain = uuidToCatalogBrain(IUUID(obj))

                if not brain:
                    # the document is trashed
                    # or not enough permission are preset to get the brain
                    continue

                # We need a BrainWrapper object to declare the item as
                # a related document for the tabbedview helper.
                brains.append(BrainWrapper(brain))

        return brains

    def get_containing_documents(self, query):
        """ Return the brains of documents created directly in a task
        """

        portal_catalog = getToolByName(self.config.context, 'portal_catalog')
        brains = portal_catalog(query)

        # We need a list and not a lazy map
        brains = [brain for brain in brains]

        return brains

    def extend_query_with_textfilter(self, brains, filter_text):
        """ Add textfiltering on brains
        """
        if not filter_text:
            return brains

        filtered_brains = []

        for brain in brains:
            text = []
            text.append(brain.Title.lower())
            text.append(brain.document_author)

            text = filter(None, text)

            if filter_text.lower() in ' '.join(text):
                filtered_brains.append(brain)

        return filtered_brains

    def extend_query_with_ordering(self, brains):
        """ Add ordering on brains
        """
        sort_index = self.request.get('sort', '')
        sort_reverse = self.config.sort_reverse
        ordered_brains = []

        if not sort_index or sort_index in ('sequence_number'):
            # currently we are not sorting or we sort it in a
            # custom_sort_method
            return brains

        if sort_index in ('document_date', 'receipt_date', 'delivery_date'):
            self.config._custom_sort_method = default_custom_sort
            return brains

        # when a transform exists for this column, we use it, since we
        # want to sort what the user is seeing.
        column = self._get_column_to_sort(self.config.columns, sort_index)
        transform = column.get('transform', None)

        if sort_index == 'sortable_title':
            transform = sortable_title_transform

        if transform:
            ordered_brains = self._sort_with_transform(
                brains, sort_index, sort_reverse, column, transform)
        else:
            ordered_brains = self._sort_with_index(
                brains, sort_index, sort_reverse)

        return ordered_brains

    def search_results(self, query):
        return query

    def _sort_with_transform(
        self, brains, sort_index, sort_reverse, column, transform):
        """ Sort the brains with a given transform-method
        """
        ordered_brains = []
        for brain in brains:
            # try to safely get the value - but it may not be needed
            # for certain transforms...
            value = getattr(brain, sort_index, None)
            if not value and column.get('column', None):
                value = getattr(brain, column.get('column'), None)

            ordered_brains.append((transform(brain, value), brain))

        # Now that we've got the sortable values for all items, sort the
        # list and then discard the values, leaving just the objects
        ordered_brains.sort(
            key=lambda item: item[0],
            reverse=sort_reverse)

        ordered_brains = [obj for val, obj in ordered_brains]

        return ordered_brains

    def _sort_with_index(self, brains, sort_index, sort_reverse):
        """ Sort the brains with a sort_index
        """
        brains.sort(key=attrgetter(sort_index), reverse=sort_reverse)
        return brains

    def _get_column_to_sort(self, columns, sort_index):
        """ Get the column-config for the given sort_index
        """
        for column in columns:

            if isinstance(column, tuple):
                continue

            if sort_index in (column.get('column', []),
                              column.get('sort_index', [])):
                return column

        return {}


class RelatedDocumentsProxy(BaseTabProxy):
    """This proxyview is looking for the last used documents
    view (list or gallery) and reopens this view.
    """
    grok.name('tabbedview_view-relateddocuments-proxy')


class RelatedDocuments(Documents):
    """Display all documents related to the given context or
    documents contained in the context
    """
    grok.name('tabbedview_view-relateddocuments')
    grok.context(ITask)
    grok.implements(IRelatedDocumentsCatalogTableSourceConfig)

    enabled_actions = [
        'send_as_email',
        'checkout',
        'checkin',
        'cancel',
        'create_task',
        'trashed',
        'send_documents',
        'copy_documents_to_remote_client',
        'move_items',
        'copy_items',
        'zip_selected',
        'export_documents',
        ]

    sort_on = 'sortable_title'

    def get_base_query(self):
        return {
            'path': {'query': '/'.join(self.context.getPhysicalPath()),
                     'depth': 2},
            'portal_type': ['opengever.document.document', 'ftw.mail.mail'],
            }
