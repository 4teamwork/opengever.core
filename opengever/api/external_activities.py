from opengever.activity import notification_center
from opengever.api.validation import get_validation_errors
from opengever.api.validation import scrub_json_payload
from opengever.base.model import SUPPORTED_LOCALES
from opengever.ogds.base.actor import ActorLookup
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.schema import ASCIILine
from zope.schema import Choice
from zope.schema import Dict
from zope.schema import List
from zope.schema import TextLine
from zope.schema import URI


class ExternalActivitiesPost(Service):

    def validate(self, data):
        scrub_json_payload(data, IExternalActivitySchema)
        errors = get_validation_errors(data, IExternalActivitySchema)
        if errors:
            raise BadRequest(errors)
        return data

    def check_authorization(self, data):
        current_userid = api.user.get_current().getId()
        recipients = data.get('notification_recipients')
        if recipients and recipients != [current_userid]:
            if not api.user.has_permission('opengever.api: Notify Arbitrary Users'):
                raise Unauthorized(
                    "Insufficient privileges to create external activities "
                    "with notification recipients other than yourself.")

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        data = json_body(self.request)
        self.check_authorization(data)

        activity_data = self.validate(data)

        errors = []

        # Resolve groups to individual users, avoiding duplicates
        recipients = set()
        for actor_id in activity_data['notification_recipients']:
            actor = ActorLookup(actor_id).lookup()
            if actor.actor_type == 'null':
                errors.append({
                    'type': 'unresolvable_actor_id',
                    'msg': 'Could not resolve Actor ID %r to a group or user' % actor_id,
                    'actor_id': actor_id,
                })
            for user in actor.representatives():
                recipients.add(user.userid)

        plone_center = notification_center()
        activity_info = plone_center.add_activity(
            obj=None,
            kind='external-activity',
            title=activity_data['title'],
            label=activity_data['label'],
            summary=activity_data['summary'],
            actor_id='__system__',
            description=activity_data['description'],
            notification_recipients=recipients,
            external_resource_url=activity_data['resource_url'],
        )

        self.request.response.setStatus(201)

        result = {}
        if activity_info:
            # We may not always get an activity_info back.
            #
            # If activity_info is None, it means an exception happened during
            # activity creation that could *not* be returned as part of
            # the 'errors' list, but got caught by the NotificationErrorHandler.
            #
            # In our case, that most likely would happen when none of the
            # passed actor_ids could be resolved, and we passed an empty
            # list to notification_recipients.
            result['activity'] = activity_info['activity'].serialize()

            not_dispatched = activity_info.get('errors', [])
            for failed_notification in not_dispatched:
                userid = failed_notification.userid
                errors.append({
                    'type': 'dispatch_failed',
                    'msg': 'Failed to dispatch notification for user %r' % userid,
                    'userid': userid,
                })

        if errors:
            result['errors'] = errors

        return result


class IExternalActivitySchema(Interface):

    notification_recipients = List(
        title=u'notification_recipients',
        value_type=ASCIILine(),
        required=True,
    )

    resource_url = URI(
        title=u'resource_url',
        required=True,
    )

    title = Dict(
        title=u'title',
        key_type=Choice(values=SUPPORTED_LOCALES),
        value_type=TextLine(),
        required=True)

    label = Dict(
        title=u'label',
        key_type=Choice(values=SUPPORTED_LOCALES),
        value_type=TextLine(),
        required=True)

    summary = Dict(
        title=u'summary',
        key_type=Choice(values=SUPPORTED_LOCALES),
        value_type=TextLine(),
        required=True)

    description = Dict(
        title=u'description',
        key_type=Choice(values=SUPPORTED_LOCALES),
        value_type=TextLine(),
        required=True)
