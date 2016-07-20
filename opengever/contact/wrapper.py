from opengever.base.wrapper import SQLWrapperBase
from opengever.contact.interfaces import IPerson
from opengever.contact.interfaces import IOrganization
from zope.interface import implements


class PersonWrapper(SQLWrapperBase):

    implements(IPerson)


class OrganizationWrapper(SQLWrapperBase):

    implements(IOrganization)
