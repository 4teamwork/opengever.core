from zope import schema
from zope.interface import Interface


class IOnlyOfficeSettings(Interface):

    enabled = schema.Bool(
        title=u"Enable OnlyOffice Integration",
        description=u"Whether the OnlyOffice integration is enabled.",
        default=False)

    documentserver_api_url = schema.TextLine(
        title=u"API Javascript URL",
        description=u"The URL of the OnlyOffice documnent server API (e.g. "
                    u"https://documentserver/web-apps/apps/api/documents/api.js)",
        default=u'',
        required=False,
    )
