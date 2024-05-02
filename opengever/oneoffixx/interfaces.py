from zope import schema
from zope.interface import Interface


class IOneoffixxSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable OneOffixx feature',
        description=u'Whether OneOffixx integration is enabled. '
                    'This feature can only be used if officeconnector is activated',
        default=False)

    template_filter_tag = schema.TextLine(
        title=u'OneOffixx tempalte filter tag',
        description=u'When filled, the TemplateFilter tag is added to the connect_xml',
        required=False)
