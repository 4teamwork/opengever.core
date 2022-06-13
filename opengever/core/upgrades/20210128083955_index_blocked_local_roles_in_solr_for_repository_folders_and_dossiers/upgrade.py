from ftw.upgrade import UpgradeStep
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.participation import IParticipationAwareMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from opengever.repository.interfaces import IRepositoryFolder


class IndexBlockedLocalRolesInSolrForRepositoryFoldersAndDossiers(UpgradeStep):
    """Index blocked_local_roles in solr for repository folders and dossiers.
    """

    deferrable = True

    def __call__(self):
        query = {'object_provides': [
            IDossierMarker.__identifier__,
            IRepositoryFolder.__identifier__,
            IDossierTemplateMarker.__identifier__,
            IParticipationAwareMarker.__identifier__
        ]}

        for obj in self.objects(query, 'Index blocked_local_roles and participation field in solr.'):
            obj.reindexObject(idxs=['blocked_local_roles', 'participations'])
