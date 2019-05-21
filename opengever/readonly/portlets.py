from plone.portlets.constants import ASSIGNMENT_SETTINGS_KEY
from plone.portlets.interfaces import IPortletAssignment, IPortletAssignmentSettings
from plone.portlets.settings import PortletAssignmentSettings
from plone.portlets.settings import portletAssignmentSettingsFactory
from zope.annotation import IAnnotations
from zope.component import adapter, queryAdapter
from zope.interface import implementer


@adapter(IPortletAssignment)
@implementer(IPortletAssignmentSettings)
def readonlyPortletAssignmentSettingsFactory(context):
    conn = context._p_jar
    if conn.isReadOnly():
        annotations = queryAdapter(context, IAnnotations)
        if ASSIGNMENT_SETTINGS_KEY not in annotations:
            # Return volatile settings
            return PortletAssignmentSettings()

    # Defer to default implementation
    return portletAssignmentSettingsFactory(context)
