from opengever.base.favorite import FavoriteManager
from opengever.base.oguid import Oguid
from opengever.core.upgrade import SQLUpgradeStep
from opengever.repository.repositoryroot import IRepositoryRoot
from plone import api
from plone.app.uuid.utils import uuidToObject
from zope.annotation.interfaces import IAnnotations


ANNOTATION_KEY = 'og-treeportlet-favorites'


class MigrateFavorites(SQLUpgradeStep):
    """Migrate favorites.
    """

    def migrate(self):
        for repo in self.repository_roots():
            storage = self.storage(repo)
            if not storage:
                continue

            for userid, uuids in storage.items():
                objs = map(uuidToObject, uuids)
                for obj in self.drop_existing(objs, userid):
                    if not obj:
                        # Object does no longer existng - skip it
                        continue

                    FavoriteManager().add(userid, obj)

            self.remove_storage(repo)

    def repository_roots(self):
        brains = api.portal.get_tool('portal_catalog').searchResults(
            object_provides=IRepositoryRoot.__identifier__)
        return [brain.getObject() for brain in brains]

    def storage(self, obj):
        return IAnnotations(obj).get(ANNOTATION_KEY)

    def remove_storage(self, obj):
        del IAnnotations(obj)[ANNOTATION_KEY]

    def drop_existing(self, objs, userid):
        """It's possible, that the current user has already defined new style
        favorites. To prevent conflicts, we do not migrate already existing
        favorites.
        """
        current_favorites = FavoriteManager().list_all_repository_favorites(userid)
        oguids = [current_favorite.oguid for current_favorite in current_favorites]
        return [obj for obj in objs if Oguid.for_object(obj) not in oguids]
