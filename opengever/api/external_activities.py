from opengever.activity import notification_center
from opengever.api.validation import get_validation_errors
from opengever.api.validation import scrub_json_payload
from opengever.base.model import SUPPORTED_LOCALES
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
        if data.get('notification_recipients') != [current_userid]:
            raise Unauthorized(
                "Insufficient privileges to create external activities with "
                "notification recipients other than yourself.")

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        data = json_body(self.request)
        self.check_authorization(data)

        activity_data = self.validate(data)

        plone_center = notification_center()
        activity_info = plone_center.add_activity(
            obj=None,
            kind='external-activity',
            title=activity_data['title'],
            label=activity_data['label'],
            summary=activity_data['summary'],
            actor_id='__system__',
            description=activity_data['description'],
            notification_recipients=activity_data['notification_recipients'],
            external_resource_url=activity_data['resource_url'],
        )

        self.request.response.setStatus(201)

        result = {}
        result['activity'] = activity_info['activity'].serialize()
        if activity_info['errors']:
            result['errors'] = activity_info['errors']

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
