from opengever.base.wrapper import SQLWrapperBase
from opengever.contact.interfaces import IPerson
from zope.interface import implements


class PersonWrapper(SQLWrapperBase):

    implements(IPerson)
