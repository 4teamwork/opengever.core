from opengever.activity.interfaces import IActivitySettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


def is_activity_feature_enabled():
    registry = getUtility(IRegistry)
    return registry.forInterface(IActivitySettings).is_feature_enabled
