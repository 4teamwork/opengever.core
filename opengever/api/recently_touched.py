from opengever.base.browser.helper import get_css_class
from opengever.base.interfaces import IRecentlyTouchedSettings
from opengever.base.touched import RECENTLY_TOUCHED_INTERFACES_TO_TRACK
from opengever.base.touched import RECENTLY_TOUCHED_KEY
from plone import api
from plone.api.portal import get_registry_record
from plone.restapi.serializer.summary import ISerializeToJsonSummary
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


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
        self._checked_out_brains = None

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

    def _get_checked_out_brains(self, user_id):
        """Returns brains of objects currently checked out by `user_id`.

        This is memoized, because its used for building both the
        'checked_out' and 'recently_touched' lists.
        """
        if self._checked_out_brains is None:
            catalog = api.portal.get_tool('portal_catalog')
            self._checked_out_brains = catalog(
                object_provides=[
                    i.__identifier__
                    for i in RECENTLY_TOUCHED_INTERFACES_TO_TRACK],
                checked_out=user_id,
                sort_on='modified',
                sort_order='reverse')
        return self._checked_out_brains

    def _get_checked_out(self, user_id):
        """Get the list of documents currently checked out by `user_id`.

        This is entirely based on information from the catalog.
        """
        # We're using the catalog's modified timestamp for these, since we
        # take care to update it on checkin/checkout
        entries = []
        for brain in self._get_checked_out_brains(user_id):
            entries.append(
                self.serialize_brain(brain, brain.modified.ISO8601()))
        return entries

    def _get_recently_touched(self, user_id):
        """Get the list of recently touched objects, minus checked out docs.

        This list is compiled by reading recently touched log for the given
        user_id, subtracting any checked out documents (because those are
        already displayed in the other list), and combining them with
        catalog brains (by UID) for any information other than the timestamp.

        Timestamps used for display and ordering are fully based on the
        recently touched log, the catalog's 'modified' timestamp isn't being
        used here.

        This is because 'modified' is a very technical timestamp,
        and it's very hard to control when it does or does not get updated.
        Therefore we use our separate timestamp when an object gets tagged
        as "touched" so we control the semantics.
        """
        portal = api.portal.get()
        catalog = api.portal.get_tool('portal_catalog')

        recently_touched_log = IAnnotations(portal).get(
            RECENTLY_TOUCHED_KEY, {}).get(user_id, [])

        # Subtract checked out docs from recently touched list
        checked_out_brains = self._get_checked_out_brains(user_id)
        checked_out_uids = [b.UID for b in checked_out_brains]
        touched_only_uids = [m['uid'] for m in recently_touched_log
                             if m['uid'] not in checked_out_uids]

        touched_brains = catalog(
            UID=touched_only_uids,
            object_provides=[i.__identifier__
                             for i in RECENTLY_TOUCHED_INTERFACES_TO_TRACK],
        )

        touched_brains_by_uid = {b.UID: b for b in touched_brains}

        entries = []
        for entry in recently_touched_log:
            brain = touched_brains_by_uid.get(entry['uid'])
            if brain is None:
                # Might have checked out docs in storage, or items that don't
                # match the currently tracked types
                continue

            entries.append(
                self.serialize_brain(brain, entry['last_touched'].isoformat()))

        # Truncate list to currently configured limit (storage might still
        # contain more entries until they get rotated out).
        limit = get_registry_record('limit', IRecentlyTouchedSettings)
        entries = entries[:limit]

        return entries

    def serialize_brain(self, brain, last_touched):
        """Serialize the brain with the summary serialization from plone restapi
        and extend the result with the two additional data `icon_class` and
        `last_touched`.
        """

        result = getMultiAdapter(
            (brain, self.request), ISerializeToJsonSummary)()
        result.update({"icon_class": get_css_class(brain),
                       "last_touched": last_touched})

        return result

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply user ID as path parameter")

        return self.params[0]
