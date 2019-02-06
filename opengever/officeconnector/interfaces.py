from zope import schema
from zope.interface import Interface


class IOfficeConnectorSettings(Interface):

    attach_to_outlook_enabled = schema.Bool(
        title=u'OfficeConnector Outlook support',
        description=u'Enable attach to Outlook with the new style '
        u'OfficeConnector URLs',
        default=True)

    direct_checkout_and_edit_enabled = schema.Bool(
        title=u'OfficeConnector direct checkout suppport',
        description=u'Enable direct checkout and edit with the new style '
        u'OfficeConnector URLs',
        default=True)

    restapi_enabled = schema.Bool(
        title=u'OfficeConnector restapi support',
        description=u'Enable sending restapi payloads Office Connector.',
        default=False)


class IOfficeConnectorSettingsView(Interface):

    def is_attach_enabled():
        pass

    def is_checkout_enabled():
        pass

    def is_restapi_enabled():
        pass
