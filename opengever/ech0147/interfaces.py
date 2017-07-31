from zope import schema
from zope.interface import Interface


class IECH0147Settings(Interface):

    ech0147_export_enabled = schema.Bool(
        title=u'Enable eCH-0147 export',
        description=u'',
        default=False)

    ech0147_import_enabled = schema.Bool(
        title=u'Enable eCH-0147 import',
        description=u'',
        default=False)
