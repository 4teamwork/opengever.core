from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from datetime import date
from opengever.activity import notification_center
from opengever.base.behaviors.classification import IClassification
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.security import elevated_privileges
from opengever.disposition import _
from opengever.disposition.appraisal import IAppraisal
from opengever.disposition.interfaces import IDisposition
from opengever.disposition.interfaces import IDuringDossierDestruction
from opengever.disposition.interfaces import IHistoryStorage
from opengever.dossier.base import DOSSIER_STATES_OFFERABLE
from opengever.dossier.behaviors.dossier import IDossier
from opengever.ogds.base.utils import get_current_admin_unit
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone import api
from plone.autoform.directives import write_permission
from plone.dexterity.content import Container
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.form import validator
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implements
from zope.intid.interfaces import IIntIds


class DossierDispositionInformation(object):
    """A wrapper object for dossiers.

    To provide easy access for the dossier's data, via the disposition
    relations list. See Disposition.get_dossier_representations.
    """

    def __init__(self, dossier, disposition):
        self.title = dossier.title
        self.intid = getUtility(IIntIds).getId(dossier)
        self.url = dossier.absolute_url()
        self.reference_number = dossier.get_reference_number()
        self.parent = aq_parent(aq_inner(dossier))
        self.start = IDossier(dossier).start
        self.end = IDossier(dossier).end
        self.public_trial = IClassification(dossier).public_trial
        self.archival_value = ILifeCycle(dossier).archival_value
        self.archival_value_annotation = ILifeCycle(dossier).archival_value_annotation
        self.appraisal = IAppraisal(disposition).get(dossier)

    @property
    def additional_metadata_available(self):
        return True

    def get_grouping_key(self):
        return self.parent

    def get_repository_title(self):
        return self.parent.Title().decode('utf-8')

    def get_storage_representation(self):
        """Returns a PersistentDict with the most important values.
        """
        return PersistentDict({
            'title': self.title,
            'intid': self.intid,
            'reference_number': self.reference_number,
            'repository_title': self.get_repository_title(),
            'appraisal': self.appraisal})


class RemovedDossierDispositionInformation(DossierDispositionInformation):

    def __init__(self, dossier_mapping, disposition):
        self.title = dossier_mapping.get('title')
        self.intid = dossier_mapping.get('intid')
        self.appraisal = dossier_mapping.get('appraisal')
        self.reference_number = dossier_mapping.get('reference_number')
        self.repository_title = dossier_mapping.get('repository_title')
        self.url = None
        self.start = None
        self.end = None
        self.public_trial = None
        self.archival_value = None
        self.archival_value_annotation = None

    @property
    def additional_metadata_available(self):
        return False

    def get_grouping_key(self):
        return self.repository_title

    def get_repository_title(self):
        return self.repository_title


def title_default():
    """Returns title suggestion in the following format:

    `Disposition {admin unit abbreviation} {localized today's date}`
    """
    return u'{} {} {}'.format(
        translate(_('label_disposition', default=u'Disposition'),
                  context=getRequest()),
        get_current_admin_unit().abbreviation,
        api.portal.get_localized_time(date.today(), long_format=False))


class IDispositionSchema(form.Schema):

    form.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[u'title', u'dossiers', u'transfer_number'],
    )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True,
        max_length=256,
        defaultFactory=title_default,
    )

    dossiers = RelationList(
        title=_(u'label_dossiers', default=u'Dossiers'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Dossier",
            source=ObjPathSourceBinder(
                object_provides=('opengever.dossier.behaviors.dossier.IDossierMarker'),
                review_state=DOSSIER_STATES_OFFERABLE,
                navigation_tree_query={
                    'object_provides':
                    ['opengever.repository.repositoryroot.IRepositoryRoot',
                     'opengever.repository.interfaces.IRepositoryFolder',
                     'opengever.dossier.behaviors.dossier.IDossierMarker'],
                }),
            ),
        required=True,
    )

    write_permission(transfer_number='opengever.disposition.EditTransferNumber')
    dexteritytextindexer.searchable('transfer_number')
    transfer_number = schema.TextLine(
        title=_(u"label_transfer_number", default=u"Transfer number"),
        required=False,
    )


class Disposition(Container):
    implements(IDisposition)

    destroyed_key = 'destroyed_dossiers'

    def __init__(self, *args, **kwargs):
        super(Disposition, self).__init__(*args, **kwargs)
        self.appraisal = {}
        self._dossiers = PersistentList()

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

    def get_history(self):
        return IHistoryStorage(self).get_history()

    def get_destroyed_dossiers(self):
        annotations = IAnnotations(self)
        if not annotations.get(self.destroyed_key):
            return None
        return annotations.get(self.destroyed_key)

    def set_destroyed_dossiers(self, dossiers):
        value = PersistentList([
            DossierDispositionInformation(dossier, self).get_storage_representation()
            for dossier in dossiers])

        IAnnotations(self)[self.destroyed_key] = value

    @property
    def is_closed(self):
        return api.content.get_state(self) == 'disposition-state-closed'

    def get_dossier_representations(self):
        if self.is_closed:
            return [RemovedDossierDispositionInformation(data, self)
                    for data in self.get_destroyed_dossiers()]

        return [DossierDispositionInformation(rel.to_object, self)
                for rel in self.dossiers]

    def update_added_dossiers(self, dossiers):
        for dossier in dossiers:
            dossier.offer()
            IAppraisal(self).initialize(dossier)

    def update_dropped_dossiers(self, dossiers):
        for dossier in dossiers:
            dossier.retract()
            IAppraisal(self).drop(dossier)

    def finalize_appraisal(self):
        """Write back the appraisal value to the dossiers.
        """
        appraisal = IAppraisal(self)
        for relation in self.dossiers:
            appraisal.write_to_dossier(relation.to_object)

    def mark_dossiers_as_archived(self):
        for relation in self.dossiers:
            api.content.transition(
                obj=relation.to_object, transition='dossier-transition-archive')

    def destroy_dossiers(self):
        alsoProvides(getRequest(), IDuringDossierDestruction)
        dossiers = [relation.to_object for relation in self.dossiers]
        self.set_destroyed_dossiers(dossiers)
        with elevated_privileges():
            api.content.delete(objects=dossiers)

    def register_watchers(self):
        center = notification_center()
        center.add_watcher_to_resource(self, self.Creator(), 'record_manager')

        for archivist in self.get_all_archivists():
            center.add_watcher_to_resource(self, archivist, 'archivist')

    def get_all_archivists(self):
        archivists = []
        acl_users = api.portal.get_tool('acl_users')
        role_manager = acl_users.get('portal_role_manager')
        for principal, title in role_manager.listAssignedPrincipals('Archivist'):
            info = role_manager.searchPrincipals(
                id=principal, exact_match=True)
            # skip not existing or duplicated groups or users
            if len(info) != 1:
                continue

            if info[0].get('principal_type') == 'group':
                group = acl_users.getGroupById(principal)
                archivists += group.getGroupMemberIds()
            else:
                archivists.append(principal)

        return archivists
