from zope import schema
from zope.interface import Interface


class IWOPISettings(Interface):

    enabled = schema.Bool(
        title=u"Enable WOPI Integration",
        description=u"Whether the WOPI integration is enabled.",
        default=False)

    discovery_url = schema.TextLine(
        title=u"WOPI Discovery URL",
        description=u"URL of the disovery endpoint.",
        default=u'https://ffc-onenote.officeapps.live.com/hosting/discovery',
        required=False,
    )
