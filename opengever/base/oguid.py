from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from opengever.ogds.base.utils import get_current_admin_unit


class Oguid(object):
    """An Oguid (OpenGever UID) uniquely identifies a Plone content object.

    This is required for deployments with multiple Plone instances since an
    IntId is only guaranteed to be unique within one Plone instance.

    This class can be used stand-alone or as an SqlAlchemy composite column
    type, see: http://docs.sqlalchemy.org/en/latest/orm/mapper_config.html.

    """
    SEPARATOR = ':'

    @classmethod
    def for_object(cls, context):
        """Create the Oguid of a Plone content object."""

        int_id = getUtility(IIntIds).getId(context)
        return cls(get_current_admin_unit().id(), int_id)

    @classmethod
    def parse(cls, oguid):
        """Parse an oguid.

        The parameter oguid must be a string in the format
        [admin_unit_id]:[int_id].

        """
        parts = oguid.split(cls.SEPARATOR)
        admin_unit_id, int_id = parts[0], int(parts[1])
        return cls(admin_unit_id, int_id)

    def __init__(self, admin_unit_id, int_id):
        self.admin_unit_id = admin_unit_id
        self.int_id = int(int_id)

    def resolve_object(self):
        if self.admin_unit_id != get_current_admin_unit().id():
            return None
        return getUtility(IIntIds).getObject(self.int_id)

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

    def __str__(self):
        return self.id
