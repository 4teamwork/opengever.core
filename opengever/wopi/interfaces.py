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

    business_user = schema.Bool(
        title=u"Business User Flow",
        description=u"Whether the business user flow is enabled.",
        default=True,
    )

    base_url = schema.TextLine(
        title=u"WOPI Base URL",
        description=u"The base URL used for WOPISrc URLs.",
        default=u'',
        required=False,
    )
