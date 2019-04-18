from ftw.builder import Builder
from ftw.builder import create
from opengever.document.versioner import Versioner
from opengever.testing import FunctionalTestCase
from plone import api
from plone.dexterity.utils import iterSchemataForType
from z3c.relationfield.interfaces import IRelationChoice
from z3c.relationfield.interfaces import IRelationList
from zc.relation.interfaces import ICatalog
from zope.component import getUtility


# Update this list when removing or adding a interface, for example a behavior.
# Because the zc.relation catalog persists provided interfaces, the catalog has
# to be cleaned up when removing an interface from this list.
# See oc.core.upgrades.CleanupICreatorInterfacesFromRelationCatalog for a howto
# example
EXPECTED_INTERFACES = [
    'AccessControl.interfaces.IOwned',
    'AccessControl.interfaces.IPermissionMappingSupport',
    'AccessControl.interfaces.IRoleManager',
    'Acquisition.interfaces.IAcquirer',
    'App.interfaces.INavigation',
    'App.interfaces.IPersistentExtra',
    'App.interfaces.IUndoSupport',
    'OFS.interfaces.ICopyContainer',
    'OFS.interfaces.ICopySource',
    'OFS.interfaces.IFTPAccess',
    'OFS.interfaces.IFindSupport',
    'OFS.interfaces.IFolder',
    'OFS.interfaces.IItem',
    'OFS.interfaces.IManageable',
    'OFS.interfaces.IObjectManager',
    'OFS.interfaces.IOrderedContainer',
    'OFS.interfaces.IPropertyManager',
    'OFS.interfaces.ISimpleItem',
    'OFS.interfaces.ITraversable',
    'OFS.interfaces.IZopeObject',
    'Products.CMFCore.interfaces._content.ICatalogAware',
    'Products.CMFCore.interfaces._content.ICatalogableDublinCore',
    'Products.CMFCore.interfaces._content.IContentish',
    'Products.CMFCore.interfaces._content.IDublinCore',
    'Products.CMFCore.interfaces._content.IDynamicType',
    'Products.CMFCore.interfaces._content.IFolderish',
    'Products.CMFCore.interfaces._content.IMinimalDublinCore',
    'Products.CMFCore.interfaces._content.IMutableDublinCore',
    'Products.CMFCore.interfaces._content.IMutableMinimalDublinCore',
    'Products.CMFCore.interfaces._content.IOpaqueItemManager',
    'Products.CMFCore.interfaces._content.IWorkflowAware',
    'Products.CMFDynamicViewFTI.interfaces.IBrowserDefault',
    'Products.CMFDynamicViewFTI.interfaces.ISelectableBrowserDefault',
    'Products.CMFEditions.interfaces.IVersioned',
    'Products.CMFPlone.interfaces.syndication.ISyndicatable',
    'collective.dexteritytextindexer.behavior.IDexterityTextIndexer',
    'collective.quickupload.interfaces.IQuickUploadCapable',
    'ftw.bumblebee.interfaces.IBumblebeeable',
    'ftw.journal.interfaces.IAnnotationsJournalizable',
    'ftw.journal.interfaces.IJournalizable',
    'ftw.tabbedview.interfaces.ITabbedView',
    'ftw.tabbedview.interfaces.ITabbedviewUploadable',
    'opengever.base.behaviors.base.IOpenGeverBaseMarker',
    'opengever.base.behaviors.changed.IChangedMarker',
    'opengever.base.behaviors.classification.IClassificationMarker',
    'opengever.base.behaviors.lifecycle.ILifeCycleMarker',
    'opengever.base.behaviors.sequence.ISequenceNumberBehavior',
    'opengever.base.behaviors.translated_title.ITranslatedTitleSupport',
    'opengever.disposition.disposition.IDispositionSchema',
    'opengever.disposition.interfaces.IDisposition',
    'opengever.document.behaviors.IBaseDocument',
    'opengever.document.behaviors.metadata.IDocumentMetadata',
    'opengever.document.document.IDocumentSchema',
    'opengever.dossier.behaviors.dossier.IDossierMarker',
    'opengever.dossier.behaviors.participation.IParticipationAwareMarker',
    'opengever.dossier.behaviors.protect_dossier.IProtectDossierMarker',
    'opengever.dossier.businesscase.IBusinessCaseDossier',
    'opengever.dossier.dossiertemplate.behaviors.IRestrictAddableDossierTemplates',
    'opengever.inbox.forwarding.IForwarding',
    'opengever.mail.behaviors.ISendableDocsContainer',
    'opengever.meeting.committee.ICommittee',
    'opengever.meeting.interfaces.IMeetingDossier',
    'opengever.meeting.proposal.IProposal',
    'opengever.meeting.proposaltemplate.IProposalTemplate',
    'opengever.meeting.sablontemplate.ISablonTemplate',
    'opengever.private.dossier.IPrivateDossier',
    'opengever.private.interfaces.IPrivateContainer',
    'opengever.quota.interfaces.IQuotaSubject',
    'opengever.quota.primary.IPrimaryBlobFieldQuota',
    'opengever.repository.behaviors.referenceprefix.IReferenceNumberPrefixMarker',
    'opengever.repository.interfaces.IRepositoryFolder',
    'opengever.repository.repositoryfolder.IRepositoryFolderSchema',
    'opengever.sharing.behaviors.IDossier',
    'opengever.task.task.ITask',
    'opengever.trash.trash.ITrashableMarker',
    'persistent.interfaces.IPersistent',
    'plone.app.lockingbehavior.behaviors.ILocking',
    'plone.app.relationfield.interfaces.IDexterityHasRelations',
    'plone.app.versioningbehavior.behaviors.IVersioningSupport',
    'plone.contentrules.engine.interfaces.IRuleAssignable',
    'plone.dexterity.interfaces.IDexterityContainer',
    'plone.dexterity.interfaces.IDexterityContent',
    'plone.dexterity.interfaces.IDexterityItem',
    'plone.folder.interfaces.IFolder',
    'plone.folder.interfaces.IOrderableFolder',
    'plone.locking.interfaces.ITTWLockable',
    'plone.namedfile.interfaces.IImageScaleTraversable',
    'plone.portlets.interfaces.ILocalPortletAssignable',
    'plone.supermodel.model.Schema',
    'plone.uuid.interfaces.IAttributeUUID',
    'plone.uuid.interfaces.IUUIDAware',
    'webdav.EtagSupport.EtagBaseInterface',
    'webdav.interfaces.IDAVCollection',
    'webdav.interfaces.IDAVResource',
    'webdav.interfaces.IWriteLock',
    'z3c.relationfield.interfaces.IHasIncomingRelations',
    'z3c.relationfield.interfaces.IHasOutgoingRelations',
    'z3c.relationfield.interfaces.IHasRelations',
    'zope.annotation.interfaces.IAnnotatable',
    'zope.annotation.interfaces.IAttributeAnnotatable',
    'zope.component.interfaces.IPossibleSite',
    'zope.container.interfaces.IContainer',
    'zope.container.interfaces.IItemContainer',
    'zope.container.interfaces.IReadContainer',
    'zope.container.interfaces.ISimpleReadContainer',
    'zope.container.interfaces.IWriteContainer',
    'zope.interface.Interface',
    'zope.interface.common.mapping.IEnumerableMapping',
    'zope.interface.common.mapping.IItemMapping',
    'zope.interface.common.mapping.IReadMapping',
    'zope.location.interfaces.IContained',
    'zope.location.interfaces.ILocation'
]


# Please update the content creation in the test below, when a new type needs
# to be added here!
EXPECTED_TYPES_WITH_RELATIONS = [
    'opengever.document.document',
    'opengever.dossier.businesscasedossier',
    'opengever.dossier.dossiertemplate',
    'opengever.repository.repositoryfolder',
    'opengever.task.task',
    'opengever.inbox.forwarding',
    'opengever.meeting.proposal',
    'opengever.meeting.submittedproposal',
    'opengever.meeting.committee',
    'opengever.meeting.sablontemplate',
    'opengever.meeting.meetingdossier',
    'opengever.meeting.proposaltemplate',
    'opengever.private.dossier',
    'opengever.disposition.disposition',
]


INTERFACE_KEYS = ['to_interfaces_flattened', 'from_interfaces_flattened']


def has_relation_fields(fti):
    for schema in iterSchemataForType(fti):
        for fieldname in schema:
            field = schema[fieldname]
            if (IRelationChoice.providedBy(field) or
                IRelationList.providedBy(field)):
                return True
    return False


class TestRelationCatalogInterfaces(FunctionalTestCase):

    def test_persisted_interfaces_in_zc_relation_catalog(self):
        root = create(Builder('repository_root').titled(u'Repository'))
        repo = create(Builder('repository')
                      .within(root)
                      .titled(u'Testposition'))

        dossier_a = create(Builder('dossier')
                           .within(repo))
        create(Builder('dossier')
               .within(repo)
               .having(relatedDossier=[dossier_a]))
        create(Builder('meeting_dossier')
               .within(repo)
               .having(relatedDossier=[dossier_a]))
        create(Builder('private_dossier')
               .within(repo)
               .having(relatedDossier=[dossier_a]))

        dossiertemplate = create(Builder('dossier')
                                 .having(relatedDossier=[dossier_a]))
        create(Builder('repository')
               .having(addable_dossier_templates=[dossiertemplate]))

        document_a = create(Builder('document').within(dossier_a))
        Versioner(document_a).create_initial_version()

        create(Builder('document').within(dossier_a).relate_to(document_a))
        create(Builder('proposaltemplate').relate_to(document_a))

        create(Builder('task').within(dossier_a).relate_to([document_a]))
        create(Builder('forwarding').within(dossier_a).relate_to([document_a]))

        sablontemplate_a = create(Builder('sablontemplate'))
        sablontemplate_b = create(Builder('sablontemplate')
                                  .relate_to(sablontemplate_a))

        create(Builder('committee_container')
               .having(protocol_header_template=sablontemplate_b))
        committee = create(Builder('committee')
                           .with_default_period()
                           .having(protocol_header_template=sablontemplate_b))

        proposal, submittedproposal = create(
            Builder('proposal')
            .having(committee=committee.load_model())
            .within(dossier_a)
            .relate_to(document_a)
            .with_submitted())

        dossier_expired = create(Builder('dossier').as_expired())
        self.grant('Records Manager')
        create(Builder('disposition').having(dossiers=[dossier_expired]))

        self.maxDiff = None
        self.assertItemsEqual(
            EXPECTED_INTERFACES, self.get_all_persisted_interfaces(),
            'Seems that a type does newly or no longer provides an interface.'
            ' Make sure if a interface has been removed, that the relation'
            ' catalog is cleaned up and adjust the EXPECTED_INTERFACES list.')

    def test_all_types_with_relations_are_handled(self):
        types_with_relations = filter(
            has_relation_fields, list(api.portal.get_tool('portal_types')))

        self.assertEquals(
            EXPECTED_TYPES_WITH_RELATIONS, types_with_relations,
            'A new type with a relation field has been introduced, please'
            ' extend the content setup with this type and adjust the expected'
            ' list EXPECTED_TYPES_WITH_RELATIONS.')

    def get_all_persisted_interfaces(self):
        catalog = getUtility(ICatalog)

        persisted_interfaces = []
        for key in INTERFACE_KEYS:
            for iface in catalog._name_TO_mapping[key].keys():
                name = '.'.join([iface.__module__, iface.__name__])
                if name not in persisted_interfaces:
                    persisted_interfaces.append(name)

        return persisted_interfaces
