from zope import schema
from zope.interface import Interface


class IDossierTemplateSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable dossier template feature',
        description=u'Whether dossier template feature is enabled or not.',
        default=False)
