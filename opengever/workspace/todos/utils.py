from plone import api
from Products.CMFPlone.utils import safe_unicode


def get_current_user_id():
    return safe_unicode(api.user.get_current().getId())
