from opengever.base.ip_range import valid_ip_range
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

    office_connector_disallowed_ip_ranges = schema.TextLine(
        title=u'IP Range from which office connecctor cannot be used '
              u'(no checkout and edit)',
        required=False,
        constraint=valid_ip_range,
        description=(
            u'IP range specification in '
            u'<strong><a href="https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing#CIDR_notation">'  # noqa
            u'CIDR notation</a></strong>. '
            u'Multiple comma-separated addresses / networks may be supplied.'),
    )


class IOfficeConnectorSettingsView(Interface):

    def is_attach_enabled():
        pass

    def is_checkout_enabled():
        pass
