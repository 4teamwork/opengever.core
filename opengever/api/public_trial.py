from opengever.base.browser.edit_public_trial import can_access_public_trial_edit_form
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services.content.update import ContentPatch
from zExceptions import Forbidden
from zExceptions import Unauthorized


PUBLIC_TRIAL_STATUS_FIELDS = ['public_trial', 'public_trial_statement']


class PublicTrialStatusPatch(ContentPatch):

    def reply(self):
        if not can_access_public_trial_edit_form(
                api.user.get_current(), self.context):
            raise Unauthorized()

        data = json_body(self.request)
        if not all(key in PUBLIC_TRIAL_STATUS_FIELDS for key in data.keys()):
            raise Forbidden(u'Only public trial fields can be edited')

        return super(PublicTrialStatusPatch, self).reply()
