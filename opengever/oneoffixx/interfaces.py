from zope import schema
from zope.interface import Interface
import json


DEFAULT_FILETYPE_TAG_MAPPING = [
    {"label": "Word", "tag": "GeverWord", "extension": "docx"},
    {"label": "Excel", "tag": "GeverExcel", "extension": "xlsx"},
    {"label": "Powerpoint", "tag": "GeverPowerpoint", "extension": "pptx"},
]


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

    filetype_tag_mapping = schema.TextLine(
        title=u'Filetypes and OneOffix tempalte tag mapping',
        description=u'Used for filetype selection in the UI',
        default=json.dumps(DEFAULT_FILETYPE_TAG_MAPPING).decode('utf-8'),
        required=False)
