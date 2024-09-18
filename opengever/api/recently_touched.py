from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_filters
from opengever.api.solrsearch import SolrSearchFieldMapper
from opengever.base.browser.helper import get_css_class
from opengever.base.interfaces import IRecentlyTouchedSettings
from opengever.base.solr import OGSolrDocument
from opengever.base.touched import RECENTLY_TOUCHED_INTERFACES_TO_TRACK
from opengever.base.touched import RECENTLY_TOUCHED_KEY
from plone import api
from plone.api.portal import get_registry_record
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.summary import DefaultJSONSummarySerializer
from plone.restapi.services import Service
from pytz import timezone
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
import dateutil


class RecentlyTouchedGet(Service):
    """API Endpoint that returns recently touched objects for a user.

    GET /@recently-touched/peter.mueller HTTP/1.1

    The endpoint returns a dictionary with two disjoint lists, one for
    currently checked out documents and one for recently touched objects.
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(RecentlyTouchedGet, self).__init__(context, request)
        self.params = []
        self._checked_out_solr_docs = None
        self.solr = getUtility(ISolrSearch)
        self._fields = None

    @property
    def fields(self):
        if not self._fields:
            fields = DefaultJSONSummarySerializer(self.context, self.request).metadata_fields()
            field_mapper = SolrSearchFieldMapper(self.solr)
            fields.update({"portal_type",
                           "getIcon",
                           "modified",
                           "file_extension",
                           "checked_out"})
            self._fields = field_mapper.get_query_fields(fields)
        return self._fields

    def publishTraverse(self, request, name):
        # Consume any path segments after /@recently-touched as parameters
        self.params.append(name)
        return self

    def reply(self):
        current_user_id = api.user.get_current().id
        if current_user_id != self.read_params():
            raise Unauthorized()

        results = {
            'checked_out': self._get_checked_out(current_user_id),
            'recently_touched': self._get_recently_touched(current_user_id),
        }
        return results

    def _get_checked_out_solr_docs(self, user_id):
        """Returns Solr docs of objects currently checked out by `user_id`.

        This is memoized, because its used for building both the
        'checked_out' and 'recently_touched' lists.
        """
        if self._checked_out_solr_docs is None:
            response = self.solr.search(
                filters=make_filters(
                    object_provides=[
                        i.__identifier__ for i in
                        RECENTLY_TOUCHED_INTERFACES_TO_TRACK],
                    checked_out=user_id,
                ),
                sort='modified desc',
                fl=self.fields,
            )
            self._checked_out_solr_docs = [OGSolrDocument(d) for d in response.docs]

        return self._checked_out_solr_docs

    def _get_checked_out(self, user_id):
        """Get the list of documents currently checked out by `user_id`.

        This is entirely based on information from Solr.
        """
        # We're using the modified timestamp from Solr for these, since we
        # take care to update it on checkin/checkout
        entries = []
        for solr_doc in self._get_checked_out_solr_docs(user_id):
            entries.append(self.serialize(solr_doc, solr_doc['modified']))
        return entries

    def _get_recently_touched(self, user_id):
        """Get the list of recently touched objects, minus checked out docs.

        This list is compiled by reading recently touched log for the given
        user_id, subtracting any checked out documents (because those are
        already displayed in the other list), and combining them with
        Solr documents (by UID) for any information other than the timestamp.

        Timestamps used for display and ordering are fully based on the
        recently touched log, the 'modified' timestamp from Solr isn't being
        used here.

        This is because 'modified' is a very technical timestamp,
        and it's very hard to control when it does or does not get updated.
        Therefore we use our separate timestamp when an object gets tagged
        as "touched" so we control the semantics.
        """
        portal = api.portal.get()

        recently_touched_log = IAnnotations(portal).get(
            RECENTLY_TOUCHED_KEY, {}).get(user_id, [])

        # Subtract checked out docs from recently touched list
        checked_out_solr_docs = self._get_checked_out_solr_docs(user_id)
        checked_out_uids = [b['UID'] for b in checked_out_solr_docs]
        touched_only_uids = [m['uid'] for m in recently_touched_log
                             if m['uid'] not in checked_out_uids]

        if touched_only_uids:
            touched_solr_docs = self.solr.search(
                filters=make_filters(
                    UID=touched_only_uids,
                    object_provides=[
                        i.__identifier__ for i in
                        RECENTLY_TOUCHED_INTERFACES_TO_TRACK],
                ),
                fl=self.fields,
            )
        else:
            return []

        touched_solr_docs_by_uid = {
            d['UID']: OGSolrDocument(d)
            for d in touched_solr_docs.docs
        }

        entries = []
        for entry in recently_touched_log:
            solr_doc = touched_solr_docs_by_uid.get(entry['uid'])
            if solr_doc is None:
                # Might have checked out docs in storage, or items that don't
                # match the currently tracked types
                continue

            entries.append(
                self.serialize(solr_doc, entry['last_touched'].isoformat()))

        # Truncate list to currently configured limit (storage might still
        # contain more entries until they get rotated out).
        limit = get_registry_record('limit', IRecentlyTouchedSettings)
        entries = entries[:limit]

        return entries

    def serialize(self, solr_doc, last_touched):
        """Serialize the OGSolrDocument with the summary serialization from
        plone restapi and extend the result with the two additional data
        `icon_class` and `last_touched`.
        """

        result = getMultiAdapter(
            (solr_doc, self.request),
            ISerializeToJsonSummary)()

        result.update({
            "icon_class": get_css_class(solr_doc),
            "last_touched": self.localize(last_touched),
            "file_extension": solr_doc.data['file_extension'],
            "checked_out": solr_doc.data['checked_out']
        })
        return result

    def localize(self, datetimestr):
        """Turn an ISO datetime string into one that is always in our
        local time, so we can provide consistency in API responses.
        """
        tz = timezone('Europe/Zurich')
        dt = dateutil.parser.parse(datetimestr)
        return dt.astimezone(tz).strftime('%Y-%m-%d %H:%M')

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply user ID as path parameter")

        return self.params[0]
