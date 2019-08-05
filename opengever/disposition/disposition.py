from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from datetime import date
from DateTime import DateTime
from opengever.activity import notification_center
from opengever.activity.roles import DISPOSITION_ARCHIVIST_ROLE
from opengever.activity.roles import DISPOSITION_RECORDS_MANAGER_ROLE
from opengever.base.behaviors.classification import IClassification
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.security import elevated_privileges
from opengever.base.source import SolrObjPathSourceBinder
from opengever.disposition import _
from opengever.disposition.appraisal import IAppraisal
from opengever.disposition.delivery import DeliveryScheduler
from opengever.disposition.ech0160.sippackage import SIPPackage
from opengever.disposition.interfaces import IDisposition
from opengever.disposition.interfaces import IDuringDossierDestruction
from opengever.disposition.interfaces import IHistoryStorage
from opengever.dossier.base import DOSSIER_STATES_OFFERABLE
from opengever.dossier.behaviors.dossier import IDossier
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone import api
from plone.autoform.directives import write_permission
from plone.dexterity.content import Container
from plone.namedfile.file import NamedBlobFile
from plone.supermodel import model
from pyxb.utils.domutils import BindingDOMSupport
from tempfile import TemporaryFile
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zExceptions import Unauthorized
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile
from zope import schema
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implements
from zope.intid.interfaces import IIntIds

DESTROY_PERMISSION = 'opengever.dossier: Destroy dossier'


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
        self.former_state = dossier.get_former_state()

    @property
    def additional_metadata_available(self):
        return True

    def get_grouping_key(self):
        return self.parent

    def was_inactive(self):
        return self.former_state == 'dossier-state-inactive'

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
            'appraisal': self.appraisal,
            'former_state': self.former_state})


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
        self.former_state = dossier_mapping.get('former_state')

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


class IDispositionSchema(model.Schema):

    model.fieldset(
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
            source=SolrObjPathSourceBinder(
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

    def get_dossiers(self):
        return [relation.to_object for relation in self.dossiers]

    def get_history(self):
        return IHistoryStorage(self).get_history()

    def get_destroyed_dossiers(self):
        annotations = IAnnotations(self)
        if not annotations.get(self.destroyed_key):
            return []
        return annotations.get(self.destroyed_key)

    def set_destroyed_dossiers(self, dossiers):
        value = PersistentList([
            DossierDispositionInformation(dossier, self).get_storage_representation()
            for dossier in dossiers])

        IAnnotations(self)[self.destroyed_key] = value

    @property
    def is_closed(self):
        return api.content.get_state(self) == 'disposition-state-closed'

    def has_dossiers_to_archive(self):
        return any(IAppraisal(self).storage.values())

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
        if not self.dossiers:
            return

        alsoProvides(getRequest(), IDuringDossierDestruction)

        dossiers = [relation.to_object for relation in self.dossiers]
        self.set_destroyed_dossiers(dossiers)
        self.check_destroy_permission(dossiers)
        with elevated_privileges():
            api.content.delete(objects=dossiers)

    def check_destroy_permission(self, dossiers):
        for dossier in dossiers:
            if not api.user.has_permission(DESTROY_PERMISSION, obj=dossier):
                raise Unauthorized()

    def register_watchers(self):
        center = notification_center()
        center.add_watcher_to_resource(
            self, self.Creator(), DISPOSITION_RECORDS_MANAGER_ROLE)

        for archivist in self.get_all_archivists():
            center.add_watcher_to_resource(
                self, archivist, DISPOSITION_ARCHIVIST_ROLE)

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
                archivists += [user.userid for user in
                               ogds_service().fetch_group(principal).users]
            else:
                archivists.append(principal)

        return archivists

    def store_sip_package(self):
        self._sip_package = self.generate_sip_package()

    def remove_sip_package(self):
        self._sip_package = None

    def generate_sip_package(self):
        package = SIPPackage(self)
        zip_file = self.create_zipfile(package)
        zip_file.seek(0)
        return NamedBlobFile(zip_file.read(), contentType='application/zip')

    def schedule_sip_for_delivery(self):
        DeliveryScheduler(self).schedule_delivery()

    def is_scheduled_for_delivery(self):
        return DeliveryScheduler(self).is_scheduled_for_delivery()

    def create_zipfile(self, package):
        tmpfile = TemporaryFile()
        BindingDOMSupport.SetDefaultNamespace(u'http://bar.admin.ch/arelda/v4')
        with ZipFile(tmpfile, 'w', ZIP_DEFLATED, True) as zipfile:
            package.write_to_zipfile(zipfile)

        return tmpfile

    def has_sip_package(self):
        return bool(self.get_sip_package())

    def get_sip_package(self):
        return getattr(self, '_sip_package', None)

    def get_sip_name(self):
        name = u'SIP_{}_{}'.format(
            DateTime().strftime('%Y%m%d'),
            api.portal.get().getId().upper())
        if self.transfer_number:
            name = u'{}_{}'.format(name, self.transfer_number)

        return name

    def get_sip_filename(self):
        return u'{}.zip'.format(self.get_sip_name())
