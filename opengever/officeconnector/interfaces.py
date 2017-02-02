from opengever.officeconnector import _
from zope import schema
from zope.interface import Interface


class IOfficeConnectorSettings(Interface):

    attach_to_outlook_enabled = schema.Bool(
        title=_(u'label_enable_officeconnector_attach_to_outlook',
                default=u'OfficeConnector Outlook support'),
        description=_(u'label_enable_officeconnector_attach_to_outlook_description', # noqa
                      default=(u'Enable attach to Outlook with the new style '
                               u'OfficeConnector URLs')),
        default=False)

    direct_checkout_and_edit_enabled = schema.Bool(
        title=_(u'label_enable_officeconnector_direct_checkout_and_edit',
                default=u'OfficeConnector direct checkout suppport'),
        description=_(u'label_enable_officeconnector_direct_checkout_and_edit_description', # noqa
                      default=(u'Enable direct checkout and edit with the '
                               u'new style OfficeConnector URLs')),
        default=False)


class IOfficeConnectorSettingsView(Interface):

    def is_attach_enabled():
        pass

    def is_checkout_enabled():
        pass
