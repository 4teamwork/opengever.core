from opengever.ogds.models.user import User
from opengever.sign.interfaces import ISignSettings
from plone import api
from sqlalchemy import func


def is_sign_feature_enabled():
    return api.portal.get_registry_record('is_feature_enabled', interface=ISignSettings)


def email_to_userid(email):
    if not email:
        return ''
    user = User.query.filter(func.lower(User.email) == email.lower()).first()
    return user.userid if user else ''
