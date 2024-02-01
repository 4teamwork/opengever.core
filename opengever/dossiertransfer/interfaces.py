from zope import schema
from zope.interface import Interface


class IDossierTransferSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable dossier transfers feature',
        description=u'Whether dossier transfers feature is enabled',
        default=False)
