from collective.elephantvocabulary import wrap_vocabulary
from DateTime import DateTime
from DateTime.interfaces import DateTimeError
from ftw.solr.converters import to_iso8601
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import escape
from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from opengever.base.helpers import display_name
from opengever.base.solr import OGSolrContentListing
from opengever.base.utils import get_preferred_language_code
from opengever.base.utils import safe_int
from opengever.globalindex.browser.report import task_type_helper as task_type_value_helper
from opengever.task.helper import task_type_helper
from plone import api
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.CMFPlone.utils import safe_unicode
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.i18n import translate
import Missing


def translate_task_type(task_type):
    return task_type_value_helper(task_type)


def translate_document_type(document_type):
    portal = getSite()
    voc = wrap_vocabulary(
            'opengever.document.document_types',
            visible_terms_from_registry='opengever.document.interfaces.'
                                        'IDocumentType.document_types')(portal)
    try:
        term = voc.getTerm(document_type)
    except LookupError:
        return document_type
    else:
        return term.title


def filesize(obj):
    try:
        filesize = obj.filesize
        if filesize != Missing.Value:
            return filesize
    except AttributeError:
        pass
    try:
        info = IPrimaryFieldInfo(obj.getObject())
    except TypeError:
        return 0
    if info.value is None:
        return 0
    return info.value.size


def filename(obj):
    try:
        filename = obj.filename
        if filename != Missing.Value:
            return filename
    except AttributeError:
        pass
    try:
        info = IPrimaryFieldInfo(obj.getObject())
    except TypeError:
        return None
    if info.value is None:
        return None
    return info.value.filename


def translated_title(obj):
    if ITranslatedTitleSupport.providedBy(obj):
        attr = 'title_{}'.format(get_preferred_language_code())
        return getattr(obj, attr, obj.Title())
    else:
        return obj.Title()


def translated_task_type(obj):
    return task_type_helper(obj, obj.get("task_type"))


def to_relative_path(value):
    portal_path_length = len(api.portal.get().getPhysicalPath())
    content_path = value.split('/')
    return '/'.join(content_path[portal_path_length:])


def relative_path(brain):
    return to_relative_path(brain.getPath())


class SimpleListingField(object):
    """Mapping between a requested field_name, the corresponding index
    in solr, the accessor on the ContentListingObject, and an index used
    when sorting according to this field.

    transform: used to cast the value of the index to a label

    additional_required_fields: used for fields that need data from
    other solr indexes on the ContentListingObject to get computed
    """

    def __init__(self, field_name):
        self.field_name = field_name
        self.index = field_name
        self.accessor = field_name
        self.sort_index = field_name
        self.transform = None
        self.additional_required_fields = []

    def listing_to_solr_filter(self, value):
        """transforms the filter value from the request to
        a filter query suitable for solr
        """
        if self.index is None:
            return
        if isinstance(value, list):
            value = map(escape, value)
            value = map(safe_unicode, value)
            value = u' OR '.join(value)
        else:
            value = escape(value)
        return u'{}:({})'.format(escape(self.index), value)

    def index_value_to_label(self, value):
        return value


class ListingField(SimpleListingField):

    def __init__(self, field_name, index, accessor=None, sort_index=None,
                 transform=None, additional_required_fields=[]):
        self.field_name = field_name
        self.index = index
        self.accessor = accessor if accessor is not None else index
        self.sort_index = sort_index if sort_index is not None else index
        self.transform = transform
        self.additional_required_fields = additional_required_fields

    def index_value_to_label(self, value):
        if self.transform is None:
            return value
        return self.transform(value)


class DateListingField(SimpleListingField):

    def _parse_dates(self, value):
        if isinstance(value, list):
            value = value[0]
        if not isinstance(value, str):
            return None, None

        dates = value.split('TO')
        if len(dates) == 2:
            try:
                date_from = DateTime(dates[0]).earliestTime()
                date_to = DateTime(dates[1]).latestTime()
            except DateTimeError:
                return None, None
        return date_from, date_to

    def listing_to_solr_filter(self, value):
        """transforms the filter value from the request to
        a filter query suitable for solr
        """
        if self.index is None:
            return
        date_from, date_to = self._parse_dates(value)
        if date_from is not None and date_to is not None:
            value = u'[{} TO {}]'.format(
                to_iso8601(date_from), to_iso8601(date_to))
        return u'{}:({})'.format(escape(self.index), value)


DEFAULT_SORT_INDEX = 'modified'

DEFAULT_FIELDS = set([
    '@id',
    '@type',
    'title',
    'description',
    'review_state',
])

FIELDS_WITH_MAPPING = [
    ListingField('checked_out', 'checked_out', transform=display_name),
    ListingField('bumblebee_checksum', 'bumblebee_checksum', sort_index=DEFAULT_SORT_INDEX),
    ListingField('checked_out', 'checked_out', transform=display_name),
    ListingField('checked_out_fullname', 'checked_out', 'checked_out_fullname'),
    ListingField('creator', 'Creator', transform=display_name),
    ListingField('description', 'Description'),
    ListingField('document_type', 'document_type', transform=translate_document_type),
    ListingField('filename', 'filename', filename),
    ListingField('filesize', 'filesize', filesize),
    ListingField('issuer_fullname', 'issuer', 'issuer_fullname'),
    ListingField('keywords', 'Subject'),
    ListingField('mimetype', 'getContentType', sort_index='mimetype'),
    ListingField('pdf_url', None, 'preview_pdf_url', DEFAULT_SORT_INDEX,
                 additional_required_fields=['bumblebee_checksum', 'path']),
    ListingField('preview_url', None, 'get_preview_frame_url', DEFAULT_SORT_INDEX,
                 additional_required_fields=['bumblebee_checksum', 'path']),
    ListingField('reference_number', 'reference'),
    ListingField('relative_path', 'path', relative_path, transform=to_relative_path),
    ListingField('responsible', 'responsible', transform=display_name),
    ListingField('responsible_fullname', 'responsible', 'responsible_fullname'),
    ListingField('review_state', 'review_state',
                 transform=lambda state: translate(
                    state, domain='plone', context=getRequest())),
    ListingField('review_state_label', 'review_state', 'translated_review_state'),
    ListingField('task_type', 'task_type', translated_task_type),
    ListingField('thumbnail_url', None, 'preview_image_url', DEFAULT_SORT_INDEX,
                 additional_required_fields=['bumblebee_checksum', 'path']),
    ListingField('title', 'Title', translated_title, 'sortable_title'),
    ListingField('type', 'portal_type', 'PortalType'),
    ListingField('@type', 'portal_type', 'PortalType'),
    ListingField('@id', "path", "getURL"),
    ]

# Add date fields to FIELDS_WITH_MAPPING
date_fields = set([
    'changed',
    'created',
    'delivery_date',
    'document_date',
    'end',
    'modified',
    'receipt_date',
    'start',
    'deadline',
])

FIELDS_WITH_MAPPING.extend(
    [DateListingField(field_name) for field_name in date_fields])


class SolrQueryBaseService(Service):

    field_mapping = {field.field_name: field for field in FIELDS_WITH_MAPPING}

    default_fields = DEFAULT_FIELDS
    required_response_fields = set()

    def __init__(self, context, request):
        super(SolrQueryBaseService, self).__init__(context, request)
        self.solr = getUtility(ISolrSearch)
        self.solr_fields = set(self.solr.manager.schema.fields.keys())
        self.default_sort_index = DEFAULT_SORT_INDEX
        self.response_fields = None

    def prepare_solr_query(self):
        """ Extract the requested parameters and prepare the solr query
        """
        params = self.request.form.copy()
        query = self.extract_query(params)
        filters = self.extract_filters(params)
        start = self.extract_start(params)
        rows = self.extract_rows(params)
        sort = self.extract_sort(params, query)
        field_list = self.extract_field_list(params)
        additional_params = self.prepare_additional_params(params)
        return query, filters, start, rows, sort, field_list, additional_params

    def extract_start(self, params):
        """Solrsearch endpoint uses start while listing endpoint uses b_start
        """
        if 'start' in params:
            start = safe_int(params.pop('start'))
        elif 'b_start' in params:
            start = safe_int(params.pop('b_start'))
        else:
            start = 0
        return start

    def extract_rows(self, params):
        """Solrsearch endpoint uses rows while listing endpoint uses b_size
        """
        if 'rows' in params:
            rows = min(safe_int(params.pop('rows'), 25), 1000)
        elif 'b_size' in params:
            rows = min(safe_int(params.pop('b_size'), 25), 1000)
        else:
            rows = 25
        return rows

    def extract_query(self, params):
        return "*:*"

    def extract_filters(self, params):
        return []

    def extract_sort(self, params, query):
        return None

    def extract_facets_from_response(self, resp):
        """Extracts facets from solr response and prepares
        counts and labels for endpoint response.
        """
        facet_counts = {}
        for field_name, facets in resp.facets.items():
            field = self.get_field(field_name)
            facet_counts[field_name] = {}
            for facet, count in facets.items():
                facet_counts[field_name][facet] = {
                    "count": count,
                    "label": field.index_value_to_label(facet)
                    }
        return facet_counts

    def parse_requested_fields(self, params):
        """Extracts requested fields from request
        """
        return []

    def extract_field_list(self, params):
        """Extracts fields from request and prepare the list
        of solr fields for the query and for the response.
        """
        requested_fields = self.parse_requested_fields(params)
        if requested_fields is not None:
            requested_fields = filter(
                self.is_field_allowed, requested_fields)
        else:
            requested_fields = self.default_fields

        self.response_fields = (set(requested_fields) |
                                self.required_response_fields)

        requested_solr_fields = set([])
        for field_name in self.response_fields:
            field = self.get_field(field_name)
            requested_solr_fields.add(field.index)
            # certain fields require data from other solr fields to be computed.
            requested_solr_fields.update(set(field.additional_required_fields))
        return list(requested_solr_fields & self.solr_fields)

    def prepare_additional_params(self, params):
        return params

    def is_field_allowed(self, field):
        return False

    def get_field(self, field_name):
        """return a ListingField for a given field_name"""
        if field_name in self.field_mapping:
            return self.field_mapping[field_name]
        return SimpleListingField(field_name)

    def get_field_index(self, field_name):
        return self.get_field(field_name).index

    def get_field_accessor(self, field_name):
        return self.get_field(field_name).accessor

    def get_field_sort_index(self, field_name):
        return self.get_field(field_name).sort_index

    def _create_list_item(self, doc):
        """Gather requested data from a ContentListingObject in a dict"""
        data = {}
        for field in self.response_fields:
            accessor = self.get_field_accessor(field)
            if isinstance(accessor, str):
                value = getattr(doc, accessor, None)
                if callable(value):
                    value = value()
            else:
                value = accessor(doc)
            data[field] = json_compatible(value)
        return data

    def prepare_response_items(self, resp):
        """Extract documents from the Sorl response and return a list
        of items containing the requested data"""
        docs = OGSolrContentListing(resp)
        items = []
        for doc in docs:
            items.append(self._create_list_item(doc))
        return items
