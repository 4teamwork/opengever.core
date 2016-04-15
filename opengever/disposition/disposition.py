from collective import dexteritytextindexer
from opengever.base.interfaces import ISequenceNumber
from opengever.disposition import _
from persistent.list import PersistentList
from plone import api
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

    destroyed_key = 'destroyed_dossiers'

    def __init__(self, *args, **kwargs):
        super(Disposition, self).__init__(*args, **kwargs)
        self.appraisal = {}
        self._dossiers = PersistentList()

    @property
    def title(self):
        return u'{} {}'.format(
            _('Disposition'), getUtility(ISequenceNumber).get_number(self))

    @title.setter
    def title(self, x):
        pass

    @property
    def dossiers(self):
        return self._dossiers

    @dossiers.setter
    def dossiers(self, value):
        old = set([rel.to_object for rel in self._dossiers])
        new = set([rel.to_object for rel in value])

        self._dossiers = value

        self.update_added_dossiers(new - old)
        self.update_dropped_dossiers(old - new)

    def update_added_dossiers(self, dossiers):
        for dossier in dossiers:
            api.content.transition(
                obj=dossier, transition='dossier-transition-offer')

    def update_dropped_dossiers(self, dossiers):
        for dossier in dossiers:
            api.content.transition(
                obj=dossier, to_state=self.get_former_state(dossier))

    def get_former_state(self, dossier):
        workflow = api.portal.get_tool('portal_workflow')
        workflow_id = workflow.getWorkflowsFor(dossier)[0].getId()
        history = workflow.getHistoryOf(workflow_id,dossier)
        return history[1].get('review_state')
