from opengever.api.validation import get_validation_errors
from opengever.ogds.models.user import User
from opengever.ogds.models.user_settings import IUserSettings
from opengever.ogds.models.user_settings import UserSettings
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.schema import getFieldsInOrder


def serialize_setting(setting):
    userid = api.user.get_current().id
    ogds_user = User.query.filter_by(userid=userid).one_or_none()
    data = {}
    for name, field in getFieldsInOrder(IUserSettings):
        # Hardcode that a pure plone users has always seen all tours.
        #
        # This is because a pure plone-user has no user-settings,
        # thus it's not possible to store seen tours. Whithout this check,
        # he would always see every tour on a pagereload
        if name == 'seen_tours' and not ogds_user:
            data[name] = [u'*']
            continue

        if setting:
            data[name] = getattr(setting, name)
        else:
            data[name] = field.default

    return data


class UserSettingsGet(Service):

    def reply(self):
        userid = api.user.get_current().id
        setting = UserSettings.query.filter_by(userid=userid).one_or_none()
        return serialize_setting(setting)


class UserSettingsPatch(Service):

    def reply(self):
        userid = api.user.get_current().id
        data = json_body(self.request)

        errors = get_validation_errors(data, IUserSettings)
        if errors:
            raise BadRequest(errors)

        setting = UserSettings.get_or_create(userid)
        for name, field in getFieldsInOrder(IUserSettings):
            if name in data:
                setattr(setting, name, data[name])

        prefer = self.request.getHeader("Prefer")
        if prefer == "return=representation":
            self.request.response.setStatus(200)
            return serialize_setting(setting)

        return self.reply_no_content()
