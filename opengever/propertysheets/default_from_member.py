from functools import partial
from plone import api
from plone.supermodel.interfaces import IDefaultFactory
from Products.CMFDiffTool.utils import safe_utf8
from Products.CMFPlone.utils import safe_unicode
from zope.globalrequest import getRequest
from zope.interface import directlyProvides
import json
import logging


logger = logging.getLogger('opengever.propertysheets')


def attach_member_property_default_factory(field, default_from_member_options):
    """Set a defaultFactory on a field to dynamically return a member property.

    Property values may be mapped via a translation table, and a fallback can
    be specified that is returned of the property value is falsy or the
    property can't be found.
    """
    factory = partial(
        member_property_default_factory, default_from_member_options)

    # Because PropertySheet widgets currently are not context aware,
    # this is not a context aware factory.
    directlyProvides(factory, IDefaultFactory)

    field.defaultFactory = factory


def member_property_default_factory(default_from_member_options):
    default_from_member_options = json.loads(default_from_member_options)

    property_name = default_from_member_options['property']
    mapping = default_from_member_options.get('mapping', {})
    fallback = default_from_member_options.get('fallback')
    allow_unmapped = default_from_member_options.get('allow_unmapped', False)

    member = api.user.get_current()

    # Extend the mapping to have both unicode and bytestring variants as keys.
    # This makes sure lookups don't miss because of unicode vs. bytestring
    # unequal comparison if the value contains non-ASCII characters.
    for source_value, target_value in mapping.items():
        if isinstance(source_value, str):
            mapping[safe_unicode(source_value)] = target_value
        if isinstance(source_value, unicode):
            mapping[safe_utf8(source_value)] = target_value

    result = None
    try:
        # use fallback for anonymous user
        if member.getUserName() == 'Anonymous User':
            return fallback

        result = member.getProperty(property_name, default=None)
        if not result:
            result = fallback

        if result in mapping:
            result = mapping[result]
        else:
            if mapping and not allow_unmapped:
                result = fallback

    except Exception as exc:
        logger.warn(
            'Failed to retrieve property %s from member %s for request %r: '
            'Got: %r' % (property_name, member, getRequest(), exc))

    if isinstance(result, str):
        # Most text-like zope.schema fields require unicode
        result = safe_unicode(result)

    return result
