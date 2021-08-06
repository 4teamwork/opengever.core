from opengever.core.upgrade import SchemaMigration
from opengever.base.model.favorite import Favorite


class FixFavoritePositions(SchemaMigration):
    """Fix favorite positions.
    """

    def migrate(self):
        users_with_favorites = [r[0] for r in self.session.query(
            Favorite.userid.distinct())]

        for userid in users_with_favorites:
            favorites = Favorite.query.by_userid(userid).order_by(
                Favorite.position)

            for i, favorite in enumerate(favorites):
                if favorite.position != i:
                    favorite.position = i
