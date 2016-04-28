from collective import dexteritytextindexer
from datetime import date
from opengever.base.behaviors.classification import IClassification
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.interfaces import ISequenceNumber
from opengever.base.security import elevated_privileges
from opengever.disposition import _
from opengever.disposition.appraisal import IAppraisal
from opengever.disposition.interfaces import IDisposition
from opengever.dossier.behaviors.dossier import IDossier
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone import api
from plone.dexterity.content import Container
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.interface import implements
from zope.interface import Invalid
from zope.interface import invariant
from zope.intid.interfaces import IIntIds


class DossierRepresentation(object):
    """A wrapper objects for dossiers.
    To provide easy access for the dossier's data via the dispositions
    relations list. See Disposition.get_dossier_representations.
    """

    def __init__(self, dossier, disposition):
        self.title = dossier.title
        self.intid = getUtility(IIntIds).getId(dossier)
        self.url = dossier.absolute_url()
        self.reference_number = dossier.get_reference_number()
        self.start = IDossier(dossier).start
        self.end = IDossier(dossier).end
        self.public_trial = IClassification(dossier).public_trial
        self.archival_value = ILifeCycle(dossier).archival_value
        self.archival_value_annotation = ILifeCycle(dossier).archival_value_annotation
        self.appraisal = IAppraisal(disposition).get(dossier)

    @property
    def additional_metadata_available(self):
        return True

    def get_storage_representation(self):
        """Returns a PersistentDict with the most important values.
        """
        return PersistentDict({
            'title': self.title,
            'intid': self.intid,
            'reference_number': self.reference_number,
            'appraisal': self.appraisal})


class RemovedDossierRepresentation(object):

    def __init__(self, dossier_mapping, disposition):
        self.title = dossier_mapping.get('title')
        self.intid = dossier_mapping.get('intid')
        self.appraisal = dossier_mapping.get('appraisal')
        self.reference_number = dossier_mapping.get('reference_number')
        self.url = None
        self.start = None
        self.end = None
        self.public_trial = None
        self.archival_value = None
        self.archival_value_annotation = None

    @property
    def additional_metadata_available(self):
        return False


class IDispositionSchema(form.Schema):

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
    implements(IDisposition)

    _dossiers = []
    destroyed_key = 'destroyed_dossiers'

    def __init__(self, *args, **kwargs):
        super(Disposition, self).__init__(*args, **kwargs)
        self.appraisal = {}

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
        return IDispositionSchema.get('dossiers').get(self)

    @dossiers.setter
    def dossiers(self, value):
        old = set([rel.to_object for rel in self._dossiers])
        new = set([rel.to_object for rel in value])

        self._dossiers = value

        self.update_added_dossiers(new - old)
        self.update_dropped_dossiers(old - new)

    def get_destroyed_dossiers(self):
        annotations = IAnnotations(self)
        if not annotations.get(self.destroyed_key):
            return None
        return annotations.get(self.destroyed_key)

    def set_destroyed_dossiers(self, dossiers):
        value = PersistentList([
            DossierRepresentation(dossier, self).get_storage_representation()
            for dossier in dossiers])

        IAnnotations(self)[self.destroyed_key] = value

    def get_dossier_representations(self):
        if api.content.get_state(self) == 'disposition-state-closed':
            return [RemovedDossierRepresentation(data, self)
                    for data in self.get_destroyed_dossiers()]

        return [DossierRepresentation(rel.to_object, self)
                for rel in self.dossiers]

    def update_added_dossiers(self, dossiers):
        for dossier in dossiers:
            ILifeCycle(dossier).date_of_submission = date.today()
            api.content.transition(
                obj=dossier, transition='dossier-transition-offer')

            IAppraisal(self).initialize(dossier)

    def update_dropped_dossiers(self, dossiers):
        for dossier in dossiers:
            ILifeCycle(dossier).date_of_submission = None
            api.content.transition(
                obj=dossier, to_state=self.get_former_state(dossier))

            IAppraisal(self).drop(dossier)

    def finalize_appraisal(self):
        """Finalize the appraisal part, means write back the appraisal value
        to the dossiers.
        """
        appraisal = IAppraisal(self)
        for relation in self.dossiers:
            appraisal.write_to_dossier(relation.to_object)

    def mark_dossiers_as_archived(self):
        for relation in self.dossiers:
            api.content.transition(
                obj=relation.to_object, transition='dossier-transition-archive')

    def get_former_state(self, dossier):
        workflow = api.portal.get_tool('portal_workflow')
        workflow_id = workflow.getWorkflowsFor(dossier)[0].getId()
        history = workflow.getHistoryOf(workflow_id,dossier)
        return history[1].get('review_state')

    def destroy_dossiers(self):
        dossiers = [relation.to_object for relation in self.dossiers]
        self.set_destroyed_dossiers(dossiers)
        with elevated_privileges():
            api.content.delete(objects=dossiers)
