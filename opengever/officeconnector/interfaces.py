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

    officeconnector_editable_types_extra = schema.List(
        title=u'Office Connector supported additional MIME types',
        description=u'A list of Office Connector supported additional MIME types.'
        u'These are additive to the default list.',
        default=[])

    officeconnector_editable_types_blacklist = schema.List(
        title=u'Office Connector supported MIME types blacklist',
        description=u'A list of Office Connector blacklisted MIME types.'
        u'These are subtractive from the default list.',
        default=[])

    attach_as_pdf_enabled = schema.Bool(
        title=u'OfficeConnector "attach as PDF" support',
        description=u'Enable attaching documents to emails as PDF.',
        default=False)


class IOfficeConnectorSettingsView(Interface):

    def is_attach_enabled():
        pass

    def is_checkout_enabled():
        pass

    def is_restapi_enabled():
        pass

    def is_attach_as_pdf_enabled():
        pass
