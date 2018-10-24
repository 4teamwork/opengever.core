from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from plone import api
from zope.globalrequest import getRequest
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('opengever.bumblebee')


BUMBLEBEE_VIEW_COOKIE_NAME = 'bumblebee-view'
SUPPORTED_CONTENT_TYPES = ['opengever.document.document',
                           'ftw.mail.mail',
                           'opengever.meeting.sablontemplate',
                           'opengever.meeting.proposaltemplate']


def is_bumblebee_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IGeverBumblebeeSettings)


def is_auto_refresh_enabled():
    return api.portal.get_registry_record(
        'is_auto_refresh_enabled', interface=IGeverBumblebeeSettings)


def set_preferred_listing_view(value):
    request = getRequest()
    request.RESPONSE.setCookie(BUMBLEBEE_VIEW_COOKIE_NAME, value, path='/')


def get_preferred_listing_view():
    request = getRequest()
    return request.cookies.get(BUMBLEBEE_VIEW_COOKIE_NAME, '')


def is_bumblebeeable(brain):
    """Return whether the brain is bumblebeeable.

    Being bumblebeeable is a decision which is made on a per content-type
    basis. Plone content-types are marked as bumblebeeable by providing a
    marker interface. There is no metadata for object_provides on a brain
    so we do a portal_type check instead.
    """
    return brain.portal_type in SUPPORTED_CONTENT_TYPES
