from collective import dexteritytextindexer
from opengever.base.interfaces import ISequenceNumber
from opengever.disposition import _
from plone.dexterity.content import Container
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.component import getUtility
from zope.interface import Invalid
from zope.interface import invariant


class IDisposition(form.Schema):

    dexteritytextindexer.searchable('reference')
    reference = schema.TextLine(
        title=_(u"label_reference", default=u"Reference"),
        description=_('help_reference', default=u""),
        required=False,
    )

    dossiers = RelationList(
        title=_(u'label_dossiers', default=u'Dossiers'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Dossier",
            source=ObjPathSourceBinder(
                object_provides=('opengever.dossier.behaviors.dossier.IDossierMarker'),
                navigation_tree_query={
                    'object_provides':
                    ['opengever.repository.repositoryroot.IRepositoryRoot',
                     'opengever.repository.interfaces.IRepositoryFolder',
                     'opengever.dossier.behaviors.dossier.IDossierMarker'],
                }),
            ),
        required=False,
    )

    @invariant
    def is_retention_period_expired(data):
        for dossier in data.dossiers:
            if not dossier.is_retention_period_expired():
                raise Invalid(
                    _(u'error_retention_period_not_expired',
                      default=u'The retention period of the selected dossiers'
                      ' is not expired.'))


class Disposition(Container):

    @property
    def title(self):
        return u'{} {}'.format(
            _('Disposition'), getUtility(ISequenceNumber).get_number(self))

    @title.setter
    def title(self, x):
        pass
