from opengever.base.exceptions import MalformedOguid
from opengever.base.exceptions import InvalidOguidIntIdPart
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.service import ogds_service
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class Oguid(object):
    """An Oguid (OpenGever UID) uniquely identifies a Plone content object.

    This is required for deployments with multiple Plone instances since an
    IntId is only guaranteed to be unique within one Plone instance.

    This class can be used stand-alone or as an SqlAlchemy composite column
    type, see: http://docs.sqlalchemy.org/en/latest/orm/mapper_config.html.

    """
    SEPARATOR = ':'

    @classmethod
    def for_object(cls, context, register=False):
        """Create the Oguid of a Plone content object.

        Optionally also register the object if on intid could be retrieved.
        This helps generating oguids for objects that are created in the same
        request and might not have an intid assigned yet.

        """
        intids = getUtility(IIntIds)
        int_id = intids.queryId(context)
        if not int_id:
            if not register:
                return None
            int_id = intids.register(context)
        return cls(get_current_admin_unit().id(), int_id)

    @classmethod
    def parse(cls, oguid):
        """Parse an oguid.

        The parameter oguid must be a string in the format
        [admin_unit_id]:[int_id].

        """
        parts = oguid.split(cls.SEPARATOR)
        if len(parts) != 2:
            raise MalformedOguid(oguid)
        admin_unit_id, int_id = parts[0], int(parts[1])
        return cls(admin_unit_id, int_id)

    def __init__(self, admin_unit_id, int_id):
        self.admin_unit_id = admin_unit_id
        self.int_id = int(int_id) if int_id else None

    def get_url(self):
        """Return an url to the object represented by this Oguid.

        Resolves the object and returns its absolute_url for objects on the
        same admin-unit.
        Returns an url to the resolve_oguid view for objects on foreign
        admin-units.

        """
        obj = self.resolve_object()
        if obj:
            return obj.absolute_url()
        admin_unit = ogds_service().fetch_admin_unit(self.admin_unit_id)

        # XXX have some kind ouf routes to avoid cyclic dependecies
        from opengever.base.browser.resolveoguid import ResolveOGUIDView
        return ResolveOGUIDView.url_for(self, admin_unit=admin_unit)

    def resolve_object(self):
        if self.admin_unit_id != get_current_admin_unit().id():
            return None
        intids = getUtility(IIntIds)
        try:
            return intids.getObject(self.int_id)
        except KeyError:
            raise InvalidOguidIntIdPart(self.int_id)

    @property
    def is_on_current_admin_unit(self):
        return self.admin_unit_id == get_current_admin_unit().id()

    @property
    def id(self):
        return self.SEPARATOR.join((self.admin_unit_id, str(self.int_id),))

    def __composite_values__(self):
        return (self.admin_unit_id, self.int_id,)

    def __eq__(self, other):
        if isinstance(other, basestring):
            return self == self.parse(other)
        return isinstance(other, Oguid) and \
            other.admin_unit_id == self.admin_unit_id and \
            other.int_id == self.int_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "<Oguid {}>".format(self.id)

    def __str__(self):
        return self.id
