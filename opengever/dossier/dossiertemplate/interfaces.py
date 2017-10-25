from zope import schema
from zope.interface import Interface


class IDossierTemplateSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable dossier template feature',
        description=u'Whether dossier template feature is enabled or not.',
        default=False)

    respect_max_depth = schema.Bool(
        title=u'Should be dossiertemplates respect the max dossier depth',
        description=u'Should the max dossier depth be strictly respected also '
        'for dossiertemplates.',
        default=False)
