from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from datetime import date
from DateTime import DateTime
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_filters
from opengever.activity import notification_center
from opengever.activity.roles import DISPOSITION_ARCHIVIST_ROLE
from opengever.activity.roles import DISPOSITION_RECORDS_MANAGER_ROLE
from opengever.base.behaviors.classification import IClassification
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.response import IResponseContainer
from opengever.base.response import IResponseSupported
from opengever.base.role_assignments import ArchivistRoleAssignment
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.security import elevated_privileges
from opengever.base.source import SolrObjPathSourceBinder
from opengever.disposition import _
from opengever.disposition.appraisal import IAppraisal
from opengever.disposition.delivery import DELIVERY_STATUS_LABELS
from opengever.disposition.delivery import DeliveryScheduler
from opengever.disposition.ech0160.sippackage import SIPPackage
from opengever.disposition.history import DispositionHistory
from opengever.disposition.interfaces import IDisposition
from opengever.disposition.interfaces import IDuringDossierDestruction
from opengever.dossier.base import DOSSIER_STATES_OFFERABLE
from opengever.dossier.behaviors.dossier import IDossier
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.service import ogds_service
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone import api
from plone.autoform.directives import write_permission
from plone.dexterity.content import Container
from plone.namedfile.file import NamedBlobFile
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.converters import json_compatible
from plone.supermodel import model
from Products.CMFPlone.CatalogTool import num_sort_regex
from Products.CMFPlone.CatalogTool import zero_fill
from Products.CMFPlone.utils import safe_hasattr
from pyxb.utils.domutils import BindingDOMSupport
from tempfile import TemporaryFile
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zExceptions import Unauthorized
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile
from zope import schema
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implements
from zope.intid.interfaces import IIntIds


DESTROY_PERMISSION = 'opengever.dossier: Destroy dossier'


def sort_on_sortable_title(item):
    if isinstance(item[0], unicode):
        return num_sort_regex.sub(zero_fill, item[0])
    return num_sort_regex.sub(zero_fill, item[0].Title())


class DossierDispositionInformation(object):
    """A wrapper object for dossiers.

    To provide easy access for the dossier's data, via the disposition
    relations list. See Disposition.get_dossier_representations.
    """

    def __init__(self, dossier, disposition):
        self.dossier = dossier
        self.disposition = disposition
        self.title = dossier.title
        self.intid = getUtility(IIntIds).getId(dossier)
        self.url = dossier.absolute_url()
        self.uid = dossier.UID()
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

    @property
    def stats(self):
        stats_by_dossier = getattr(self.disposition, 'stats_by_dossier', {})
        return stats_by_dossier.get(self.dossier.UID(), {})

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

    def jsonify(self):
        return json_compatible({
            'title': self.title,
            'intid': self.intid,
            'appraisal': self.appraisal,
            'reference_number': self.reference_number,
            'url': self.url,
            'uid': self.uid,
            'start': self.start,
            'end': self.end,
            'public_trial': self.serialize_public_trial(),
            'archival_value': self.serialize_archival_value(),
            'archival_value_annotation': self.archival_value_annotation,
            'former_state': self.former_state,
            'docs_count': self.stats.get('docs_count'),
            'docs_size': self.stats.get('docs_size'),
        })

    def serialize_public_trial(self):
        if not self.public_trial:
            return

        serializer = getMultiAdapter(
            (IClassification['public_trial'], self.dossier, getRequest()),
            IFieldSerializer)
        return serializer()

    def serialize_archival_value(self):
        if not self.archival_value:
            return

        serializer = getMultiAdapter(
            (ILifeCycle['archival_value'], self.dossier, getRequest()),
            IFieldSerializer)
        return serializer()


class RemovedDossierDispositionInformation(DossierDispositionInformation):

    def __init__(self, dossier_mapping, disposition):
        self.title = dossier_mapping.get('title')
        self.intid = dossier_mapping.get('intid')
        self.appraisal = dossier_mapping.get('appraisal')
        self.reference_number = dossier_mapping.get('reference_number')
        self.repository_title = dossier_mapping.get('repository_title')
        self.url = None
        self.uid = None
        self.start = None
        self.end = None
        self.public_trial = None
        self.archival_value = None
        self.archival_value_annotation = None
        self.former_state = dossier_mapping.get('former_state')

    @property
    def stats(self):
        return {}

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


def transferring_office_default():
    return get_current_admin_unit().label()


class IDispositionSchema(model.Schema):

    model.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[u'title', u'dossiers', u'transfer_number', u'transferring_office'],
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

    transferring_office = schema.TextLine(
        title=_(u"label_transferring_office", default=u"Transferring office"),
        required=False,
        defaultFactory=transferring_office_default
    )


class Disposition(Container):
    implements(IDisposition, IResponseSupported)

    destroyed_key = 'destroyed_dossiers'
    creation_activity_recorded_key = 'creation_activity_recorded'

    def __init__(self, *args, **kwargs):
        super(Disposition, self).__init__(*args, **kwargs)
        self.appraisal = {}
        self.stats_by_dossier = PersistentDict()

        self._dossiers = PersistentList()
        self._dossiers_with_missing_permissions = PersistentList()
        self._dossiers_with_extra_permissions = PersistentList()

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

    def get_dossiers_with_positive_appraisal(self):
        appraisal = IAppraisal(self)
        return [dossier for dossier in self.get_dossiers() if appraisal.get(dossier)]

    def get_history(self):
        history = [DispositionHistory.get(response)
                   for response in IResponseContainer(self)]
        history.reverse()
        return history

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
    def dossiers_with_missing_permissions(self):
        return self._dossiers_with_missing_permissions

    @dossiers_with_missing_permissions.setter
    def dossiers_with_missing_permissions(self, dossiers):
        self._dossiers_with_missing_permissions = PersistentList(dossiers)

    @property
    def dossiers_with_extra_permissions(self):
        return self._dossiers_with_extra_permissions

    @dossiers_with_extra_permissions.setter
    def dossiers_with_extra_permissions(self, dossiers):
        self._dossiers_with_extra_permissions = PersistentList(dossiers)

    @property
    def has_dossiers_with_pending_permissions_changes(self):
        return bool(self.dossiers_with_missing_permissions or self.dossiers_with_extra_permissions)

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

    def get_grouped_dossier_representations(self):
        dossiers = self.get_dossier_representations()
        inactive_dossiers = {}
        active_dossiers = {}

        for dossier in dossiers:
            if dossier.was_inactive():
                self._add_to(inactive_dossiers, dossier)
            else:
                self._add_to(active_dossiers, dossier)

        return (
            sorted(active_dossiers.items(), key=sort_on_sortable_title),
            sorted(inactive_dossiers.items(), key=sort_on_sortable_title))

    def _add_to(self, mapping, dossier):
        key = dossier.get_grouping_key()
        mapping.setdefault(key, []).append(dossier)

    def update_added_dossiers(self, dossiers):
        self.update_stats_by_dossier(dossiers)

        for dossier in dossiers:
            dossier.offer()
            IAppraisal(self).initialize(dossier)
            # Remember which dossiers need their permissions updated
            uid = dossier.UID()
            if uid in self.dossiers_with_extra_permissions:
                # if that dossier was dropped before but its permissions
                # not updated yet, then its permissions are already correct
                self.dossiers_with_extra_permissions.remove(uid)
            else:
                self.dossiers_with_missing_permissions.append(uid)

    def update_dropped_dossiers(self, dossiers):
        for dossier in dossiers:
            dossier.retract()
            IAppraisal(self).drop(dossier)

            uid = dossier.UID()
            if safe_hasattr(self, 'stats_by_dossier'):
                self.stats_by_dossier.pop(uid, None)

            # Remember which dossiers need their permissions updated
            if uid in self.dossiers_with_missing_permissions:
                # if that dossier was added before but its permissions
                # not updated yet, then its permissions are already correct
                self.dossiers_with_missing_permissions.remove(uid)
            else:
                self.dossiers_with_extra_permissions.append(uid)

    def update_stats_by_dossier(self, dossiers):
        if not safe_hasattr(self, 'stats_by_dossier'):
            self.stats_by_dossier = PersistentDict()

        for dossier in dossiers:
            stats = self.query_stats(dossier)
            self.stats_by_dossier[dossier.UID()] = PersistentDict(stats)

    def query_stats(self, dossier):
        solr = getUtility(ISolrSearch)

        filters = make_filters(
            path_parent='/'.join(dossier.getPhysicalPath()),
            portal_type=['ftw.mail.mail', 'opengever.document.document'],
        )
        params = {
            'stats': 'true',
            'stats.field': ['{!sum=true}filesize'],
        }

        resp = solr.search(query='*', filters=filters, fl=['path'], **params)
        return {
            'docs_count': resp.body['response']['numFound'],
            'docs_size': int(resp.body['stats']['stats_fields']['filesize']['sum']),
        }

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

    @staticmethod
    def get_archivists_infos():
        archivists = []
        acl_users = api.portal.get_tool('acl_users')
        role_manager = acl_users.get('portal_role_manager')
        for principal, title in role_manager.listAssignedPrincipals('Archivist'):

            info = role_manager.searchPrincipals(
                id=principal, exact_match=True)
            # skip not existing or duplicated groups or users
            if len(info) != 1:
                continue
            archivists.append((principal, info))

        return archivists

    def get_all_archivists(self):
        archivists_infos = self.get_archivists_infos()
        archivists = []
        for principal, info in archivists_infos:
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

    def sip_download_available(self):
        if api.user.has_permission(
                'opengever.disposition: Download SIP Package', obj=self):

            return self.has_sip_package()

        return None

    def removal_protocol_available(self):
        return api.content.get_state(self) == 'disposition-state-closed'

    def get_delivery_status_infos(self):
        """Get translated delivery status infos in a template friendly format.
        """
        statuses = DeliveryScheduler(self).get_statuses()
        status_infos = [
            {'name': n, 'status': translate(DELIVERY_STATUS_LABELS[s], context=getRequest())}
            for n, s in statuses.items()]
        return status_infos

    def give_view_permissions_to_archivists_on_dossier(self, dossier):
        """We need to give permissions on the dossier but also on the
        subdossiers with blocked inheritance
        """
        assignments = [ArchivistRoleAssignment(principal, ["Reader"], self)
                       for principal, info in self.get_archivists_infos()]

        RoleAssignmentManager(dossier).add_or_update_assignments(assignments)

        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            path='/'.join(dossier.getPhysicalPath()),
            blocked_local_roles=True)

        for brain in brains:
            obj = brain._unrestrictedGetObject()
            if obj != dossier and obj is not None:
                RoleAssignmentManager(obj).add_or_update_assignments(assignments)

    def revoke_view_permissions_from_archivists_on_dossier(self, dossier):
        """We clear the permissions on the dossier and all subdossiers
        """
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            path='/'.join(dossier.getPhysicalPath()))
        for brain in brains:
            obj = brain._unrestrictedGetObject()
            manager = RoleAssignmentManager(obj)
            if manager.get_assignments_by_reference(self):
                manager.clear_by_reference(self)

    @property
    def creation_activity_recorded(self):
        return IAnnotations(self).get(self.creation_activity_recorded_key, False)

    @creation_activity_recorded.setter
    def creation_activity_recorded(self, value):
        IAnnotations(self)[self.creation_activity_recorded_key] = value
