from copy import deepcopy
from DateTime import DateTime
from DateTime.interfaces import DateTimeError
from ftw.solr.converters import to_iso8601
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import escape
from opengever.api.utils import recursive_encode
from opengever.base.behaviors.translated_title import TRANSLATED_TITLE_PORTAL_TYPES
from opengever.base.helpers import display_name
from opengever.base.solr import OGSolrContentListing
from opengever.base.utils import get_preferred_language_code
from opengever.base.utils import safe_int
from opengever.base.vocabulary import wrap_vocabulary
from opengever.dossier.indexers import ParticipationIndexHelper
from opengever.globalindex.browser.report import task_type_helper as task_type_value_helper
from opengever.propertysheets.definition import SolrDynamicField
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.task.helper import task_type_helper
from opengever.tasktemplates.content.templatefoldersschema import sequence_type_vocabulary
from plone import api
from plone.memoize.view import memoize
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.CMFPlone.utils import safe_unicode
from Products.ZCatalog.Lazy import LazyMap
from zExceptions import BadRequest
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.i18n import translate
import Missing


def filter_escape(term):
    """If there is a space in the term, then quotation marks are required around the term
    """
    if isinstance(term, bool):
        return term
    term = escape(term)
    if ' ' in term:
        term = '"{}"'.format(term)
    return term


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


def translate_dossier_type(dossier_type):
    portal = getSite()
    voc = wrap_vocabulary(
        'opengever.dossier.dossier_types',
        hidden_terms_from_registry='opengever.dossier.interfaces.IDossierType.hidden_dossier_types')(portal)
    try:
        term = voc.getTerm(dossier_type)
    except LookupError:
        return dossier_type
    else:
        return term.title


def translate_sequence_type(sequence_type):
    return translate(sequence_type_vocabulary.getTerm(sequence_type).title,
                     context=getRequest(),
                     domain="opengever.tasktemplates")


def translate_public_trial(public_trial):
    return translate(public_trial, context=getRequest(), domain="opengever.base")


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
    if obj.portal_type in TRANSLATED_TITLE_PORTAL_TYPES:
        return obj.getObject().Title(language=get_preferred_language_code())
    else:
        return obj.Title()


def translated_task_type(obj):
    return task_type_helper(obj, obj.get("task_type"))


def translated_document_type_label(obj):
    portal = getSite()
    voc = wrap_vocabulary(
            'opengever.document.document_types',
            visible_terms_from_registry='opengever.document.interfaces.'
                                        'IDocumentType.document_types')(portal)
    try:
        term = voc.getTerm(obj.get("document_type"))
    except LookupError:
        return None
    return term.title


def translated_dossier_type_label(obj):
    portal = getSite()
    voc = wrap_vocabulary(
        'opengever.dossier.dossier_types',
        hidden_terms_from_registry='opengever.dossier.interfaces.IDossierType.hidden_dossier_types')(portal)
    try:
        term = voc.getTerm(obj.get("dossier_type"))
    except LookupError:
        return None
    return term.title


def translated_public_trial(obj):
    try:
        return translate(obj.public_trial, context=getRequest(), domain="opengever.base")
    except AttributeError:
        return None


def translated_sequence_type(obj):
    try:
        term = sequence_type_vocabulary.getTerm(obj.sequence_type)
    except LookupError:
        return None
    return term.title


def to_relative_path(value):
    portal_path_length = len(api.portal.get().getPhysicalPath())
    content_path = value.split('/')
    return '/'.join(content_path[portal_path_length:])


def relative_path(brain):
    return to_relative_path(brain.getPath())


def relative_to_physical_path(relative_path):
    """A frontend usualy only knows the relative path to the plone site,
    not the real physical path of an object.
    But the solr index value contains the physical path of
    the object. Thus, we need to replace the relative paths with the physical
    path of an object.
    """
    physical_path = api.portal.get().getPhysicalPath()
    relative_path = relative_path.strip('/')
    if relative_path:
        physical_path += (relative_path, )

    return '/'.join(physical_path)


def url_to_physical_path(value):
    portal_url = api.portal.get().absolute_url()
    return relative_to_physical_path(value.replace(portal_url, ''))


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
            value = map(filter_escape, value)
            value = map(safe_unicode, value)
            value = u' OR '.join(value)
        else:
            value = filter_escape(safe_unicode(value))

        # Convert python empty string to solr empty string
        if value == u'':
            value = u'""'

        # Escaping the Solr field name is done for security reasons
        # (to prevent attempts to circumvent the security filter by injection
        # of a maliciously crafted field name)
        key = filter_escape(self.index)
        # Don't escape the '-' at the beginning as it's used to negate a filter query
        if key.startswith('\\-'):
            key = key[1:]

        return u'{}:({})'.format(key, value)

    def index_value_to_label(self, value):
        return value

    def hide_facet(self, facet):
        return False


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

    @staticmethod
    def _to_solr_date_string(value, rounding_function):
        value = value.strip()
        if value == "*":
            return value
        try:
            return to_iso8601(getattr(DateTime(value), rounding_function)())
        except DateTimeError:
            raise BadRequest("Could not parse date: {}".format(value))

    def _parse_dates(self, value):
        if isinstance(value, list):
            value = value[0]
        if not isinstance(value, str):
            return None, None

        dates = value.split('TO')

        if len(dates) == 2:
            date_from = self._to_solr_date_string(dates[0], 'earliestTime')
            date_to = self._to_solr_date_string(dates[1], 'latestTime')
            return date_from, date_to
        raise BadRequest("Only date ranges are supported: {}".format(value))

    def listing_to_solr_filter(self, value):
        """transforms the filter value from the request to
        a filter query suitable for solr
        """
        if self.index is None:
            return
        date_from, date_to = self._parse_dates(value)
        if date_from is not None and date_to is not None:
            value = u'[{} TO {}]'.format(date_from, date_to)
        return u'{}:({})'.format(filter_escape(self.index), value)


class ParticipationsField(ListingField):

    field_name = 'participations'

    def __init__(self):
        self.index = 'participations'
        self.sort_index = self.index
        self.additional_required_fields = []
        self.helper = ParticipationIndexHelper()

    def accessor(self, doc):
        if not doc.get('participations'):
            return
        return list({self.index_value_to_label(participation)
                     for participation in doc.get('participations')})

    def index_value_to_label(self, value):
        return self.helper.index_value_to_label(value)


class ParticipantIdField(ParticipationsField):

    field_name = 'participants'

    def index_value_to_label(self, value):
        participant_id = self.helper.index_value_to_participant_id(value)
        return self.helper.participant_id_to_label(participant_id)

    def hide_facet(self, facet):
        return self.helper.index_value_to_role(facet) != self.helper.any_role_marker


class ParticipationRoleField(ParticipationsField):

    field_name = 'participation_roles'

    def index_value_to_label(self, value):
        role = self.helper.index_value_to_role(value)
        return self.helper.role_to_label(role)

    def hide_facet(self, facet):
        return self.helper.index_value_to_participant_id(facet) != self.helper.any_participant_marker


DEFAULT_SORT_INDEX = 'modified'

DEFAULT_FIELDS = set([
    '@id',
    '@type',
    'title',
    'description',
    'review_state',
])

# UID is necessary when requesting snippets
REQUIRED_RESPONSE_FIELDS = set(['UID'])

FIELDS_WITH_MAPPING = [
    ListingField('bumblebee_checksum', 'bumblebee_checksum', sort_index=DEFAULT_SORT_INDEX),
    ListingField('checked_out', 'checked_out', transform=display_name),
    ListingField('checked_out_fullname', 'checked_out', 'checked_out_fullname'),
    ListingField('creator', 'Creator', transform=display_name),
    ListingField('creator_fullname', 'Creator', 'creator_fullname'),
    ListingField('description', 'Description'),
    ListingField('document_type', 'document_type', transform=translate_document_type),
    ListingField('document_type_label', 'document_type', accessor=translated_document_type_label),
    ListingField('dossier_type', 'dossier_type', transform=translate_dossier_type),
    ListingField('dossier_type_label', 'dossier_type', accessor=translated_dossier_type_label),
    ListingField('filename', 'filename', filename),
    ListingField('filesize', 'filesize', filesize),
    ListingField('issuer', 'issuer', transform=display_name),
    ListingField('issuer_fullname', 'issuer', 'issuer_fullname'),
    ListingField('keywords', 'Subject'),
    ListingField('mimetype', 'getContentType', sort_index='mimetype'),
    ParticipationsField(),
    ParticipantIdField(),
    ParticipationRoleField(),
    ListingField('pdf_url', None, 'preview_pdf_url', DEFAULT_SORT_INDEX,
                 additional_required_fields=['bumblebee_checksum', 'path', 'portal_type']),
    ListingField('preview_url', None, 'get_preview_frame_url', DEFAULT_SORT_INDEX,
                 additional_required_fields=['bumblebee_checksum', 'path', 'portal_type']),
    ListingField('public_trial', 'public_trial', accessor=translated_public_trial,
                 transform=translate_public_trial),
    ListingField('reference_number', 'reference', sort_index='sortable_reference'),
    ListingField('reference', 'reference', sort_index='sortable_reference'),
    ListingField('relative_path', 'path', relative_path, transform=to_relative_path),
    ListingField('responsible', 'responsible', transform=display_name),
    ListingField('responsible_fullname', 'responsible', 'responsible_fullname'),
    ListingField('review_state', 'review_state',
                 transform=lambda state: translate(
                    state, domain='plone', context=getRequest())),
    ListingField('review_state_label', 'review_state', 'translated_review_state'),
    ListingField('sequence_type', 'sequence_type', accessor=translated_sequence_type,
                 transform=translate_sequence_type),
    ListingField('task_type', 'task_type', accessor=translated_task_type, transform=translate_task_type),
    ListingField('thumbnail_url', None, 'preview_image_url', DEFAULT_SORT_INDEX,
                 additional_required_fields=['bumblebee_checksum', 'path']),
    ListingField('title', 'Title', translated_title, 'sortable_title',
                 additional_required_fields=['portal_type']),
    ListingField('type', 'portal_type', 'PortalType'),
    ListingField('@type', 'portal_type', 'PortalType'),
    ListingField('@id', "path", "getURL"),
    ]

# Add date fields to FIELDS_WITH_MAPPING
date_fields = set([
    'changed',
    'created',
    'deadline',
    'delivery_date',
    'document_date',
    'end',
    'modified',
    'receipt_date',
    'retention_expiration',
    'start',
    'touched',
])

FIELDS_WITH_MAPPING.extend(
    [DateListingField(field_name) for field_name in date_fields])

# Currently, operators and field names are not separated when determining the field.
# Therefore the correct field is not found when a negating filter is queried (e.g. "-keywords")
# To get the correct field for negating filters,
# all fields are copied and a "-" is placed at the beginning of the field name and index.
copied_fields = deepcopy(FIELDS_WITH_MAPPING)
for field in copied_fields:
    field.field_name = '-' + field.field_name
    field.index = '-' + field.index if field.index else None
FIELDS_WITH_MAPPING.extend(copied_fields)


class SolrFieldMapper(object):

    field_mapping = {field.field_name: field for field in FIELDS_WITH_MAPPING}

    default_fields = DEFAULT_FIELDS
    required_response_fields = REQUIRED_RESPONSE_FIELDS

    def __init__(self, solr):
        self.all_solr_fields = set(
            solr.manager.schema.fields.keys()
            + self.get_custom_property_fields()
        )

    def get(self, field_name):
        """Return a ListingField for a given field_name.
        """
        if field_name in self.field_mapping:
            return self.field_mapping[field_name]
        return SimpleListingField(field_name)

    def is_allowed(self, field_name):
        """Whether or not a field is allowed to be queried.
        """
        return False

    def build_field_list(self, requested_fields):
        """Builds the list of fields to be queried from Solr.

        Based on the given list of requested fields, build the effective list
        by considering that

        - not all fields are allowed to be queried
        - some fields need additional fields to be computed
        - some fields are dynamic (custom properties)
        - some fields are always required in the response

        In addition, a list of fields that should be present in the response
        is returned.
        """
        if requested_fields is not None:
            requested_fields = filter(self.is_allowed, requested_fields)
        else:
            requested_fields = self.default_fields

        response_fields = (set(requested_fields) | self.required_response_fields)

        dynamic_fields = []
        requested_solr_fields = set([])
        for field_name in response_fields:
            field = self.get(field_name)
            requested_solr_fields.add(field.index)

            # Certain fields require data from other Solr fields to be computed.
            requested_solr_fields.update(set(field.additional_required_fields))

            if SolrDynamicField.is_dynamic_field(field_name):
                dynamic_fields.append(field_name)

        query_field_list = list(requested_solr_fields & self.all_solr_fields) + dynamic_fields
        response_field_list = response_fields
        return query_field_list, response_field_list

    def get_custom_property_fields(self):
        """Get the list of dynamic Solr fields used for custom properties.
        """
        solr_fields = []

        storage = PropertySheetSchemaStorage()
        if not storage:
            return solr_fields

        for definition in storage.list():
            if definition is not None:
                schema = definition.get_solr_dynamic_field_schema()
                solr_fields.extend(schema.keys())

        return solr_fields


class SolrQueryBaseService(Service):

    field_mapper = SolrFieldMapper

    def __init__(self, context, request):
        super(SolrQueryBaseService, self).__init__(context, request)
        self.solr = getUtility(ISolrSearch)
        self.fields = self.field_mapper(self.solr)

        self.default_sort_index = DEFAULT_SORT_INDEX
        self.response_fields = None
        self.facets = []

    @property
    @memoize
    def request_payload(self):
        """Returns the request payload depending on the http request method.
        """
        if self.request.method == 'GET':
            return self.request.form
        elif self.request.method == 'POST':
            # JSON always returns unicode strings. We need to encode the values
            # to utf-8 to get the same encoding as with a GET reqeust.
            return recursive_encode(json_body(self.request))

    def prepare_solr_query(self):
        """ Extract the requested parameters and prepare the solr query
        """
        params = self.request_payload.copy()
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
        for facet_name in self.facets:
            field = self.fields.get(facet_name)
            solr_facet_name = field.index
            solr_facet = resp.facets.get(solr_facet_name)

            if not solr_facet:
                continue

            facet_counts[facet_name] = {}
            for facet, count in solr_facet.items():
                if field.hide_facet(facet):
                    continue
                facet_counts[field.field_name][facet] = {
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
        query_field_list, response_field_list = self.fields.build_field_list(requested_fields)
        self.response_fields = response_field_list
        return query_field_list

    def extract_depth(self, params):
        """If depth is not specified we search recursively
        """
        # By default search recursively
        depth = params.get('depth', -1)
        try:
            depth = int(depth)
        except ValueError:
            raise BadRequest("Could not parse depth: {}".format(depth))
        return depth

    def prepare_additional_params(self, params):
        return params

    def _create_list_item(self, doc):
        """Gather requested data from a ContentListingObject in a dict"""
        data = {}
        for field in self.response_fields:
            accessor = self.fields.get(field).accessor
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

    def extend_with_batching(self, response, solr_response):
        """Extends the current response-dict with batching links
        """
        # We use the HypermediaBatch only to generate the links,
        # we therefore do not need the real sequence of objects here
        items = LazyMap(None, [], actual_result_count=solr_response.num_found)
        batch = HypermediaBatch(self.request, items)

        response['@id'] = batch.canonical_url
        response['items_total'] = batch.items_total
        if batch.links:
            response['batching'] = batch.links
