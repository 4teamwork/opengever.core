from ftw.bumblebee.utils import get_representation_url_by_brain as representation_url_by_brain
from ftw.bumblebee.utils import get_representation_url_by_object as representation_url_by_object
from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from plone import api
from zope.globalrequest import getRequest

BUMBLEBEE_VIEW_COOKIE_NAME = 'bumblebee-view'


def get_not_digitally_available_placeholder_image_url():
    return "{}{}".format(
        api.portal.get().absolute_url(),
        "/++resource++opengever.base/images/not_digitally_available.png")


def is_bumblebee_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IGeverBumblebeeSettings)


def get_representation_url_by_object(format_name, obj):
    """Returns the bumblebee representation url of the object.

    Bumblebee will return the representation if the obj has a checksum.
    The checksum is only available if the obj has an attached document.

    If no checksum is available, the representation_url will be none.

    That means, our obj is only preserved as paper and we have to return
    a special placeholder image for these documents
    """
    return representation_url_by_object(format_name, obj) or \
        get_not_digitally_available_placeholder_image_url()


def get_representation_url_by_brain(format_name, brain):
    """Returns the bumblebee representation url of the brain.

    Bumblebee will return the representation if the brain has a checksum.
    The checksum is only available if the brain has an attached document.

    If no checksum is available, the representation_url will be none.

    That means, our brain is only preserved as paper and we have to return
    a special placeholder image for these documents
    """
    return representation_url_by_brain(format_name, brain) or \
        get_not_digitally_available_placeholder_image_url()


def set_prefered_listing_view(value):
    request = getRequest()
    request.RESPONSE.setCookie(BUMBLEBEE_VIEW_COOKIE_NAME, value, path='/')


def get_prefered_listing_view():
    request = getRequest()
    return request.cookies.get(BUMBLEBEE_VIEW_COOKIE_NAME, '')


def is_bumblebeeable(brain):
    """Return whether the brain has a bumblebee_checksum.

    The checksum is only available for objects that provide IBumblebeeable,
    so we use it to detect if a brain's object is IBumblebeeable without
    loading the object.
    """
    return bool(brain.bumblebee_checksum)
