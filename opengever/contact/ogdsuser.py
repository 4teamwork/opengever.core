from opengever.ogds.base.utils import ogds_service
from opengever.ogds.base.browser.userdetails import UserDetails


class OgdsUserAdapter(object):
    """Adapter that represents ogds users as sql-contacts."""

    class QueryAdapter(object):
        """Adapter for query calls."""

        def get(self, userid):
            return OgdsUserAdapter(ogds_service().find_user(userid))
    query = QueryAdapter()

    def __init__(self, ogds_user):
        self.ogds_user = ogds_user

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash(self.id)

    @property
    def id(self):
        return self.ogds_user.userid

    def get_title(self, with_former_id=None):
        return self.ogds_user.label()

    def get_url(self):
        return UserDetails.url_for(self.id)

    def get_css_class(self):
        return 'contenttype-person'
