from opengever.ogds.models import BASE
from opengever.ogds.models import EMAIL_LENGTH
from opengever.ogds.models import FIRSTNAME_LENGTH
from opengever.ogds.models import LASTNAME_LENGTH
from opengever.ogds.models import USER_ID_LENGTH
from opengever.ogds.models.query import BaseQuery
from opengever.ogds.models.types import UnicodeCoercingText
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import String


class UserQuery(BaseQuery):

    searchable_fields = ['userid', 'firstname', 'lastname', 'email']


class User(BASE):
    """User model
    """

    query_cls = UserQuery

    __tablename__ = 'users'

    userid = Column(String(USER_ID_LENGTH), primary_key=True)
    active = Column(Boolean, default=True)
    firstname = Column(String(FIRSTNAME_LENGTH))
    lastname = Column(String(LASTNAME_LENGTH))

    directorate = Column(String(255))
    directorate_abbr = Column(String(50))
    department = Column(String(255))
    department_abbr = Column(String(50))

    email = Column(String(EMAIL_LENGTH))
    email2 = Column(String(EMAIL_LENGTH))
    url = Column(String(100))
    phone_office = Column(String(30))
    phone_fax = Column(String(30))
    phone_mobile = Column(String(30))

    salutation = Column(String(30))
    description = Column(UnicodeCoercingText())
    address1 = Column(String(100))
    address2 = Column(String(100))
    zip_code = Column(String(10))
    city = Column(String(100))

    country = Column(String(20))

    import_stamp = Column(String(26))

    def __init__(self, userid, **kwargs):
        self.userid = userid
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return '<User %s>' % self.userid

    def __eq__(self, other):
        if isinstance(other, User):
            return self.userid == other.userid
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def label(self, with_principal=True):
        if not with_principal:
            return self.fullname()

        return "%s (%s)" % (self.fullname(), self.userid)

    def fullname(self):
        """return a visual representation of the UserPersona as String.
             - The default is "<lastname> <firstname>"
             - If either one is missing it is: "<lastname>" or "<firstname>"
             - The fallback is "<userid>"
        """
        parts = []
        self.lastname and parts.append(self.lastname)
        self.firstname and parts.append(self.firstname)
        len(parts) == 0 and parts.append(self.userid)

        return ' '.join(parts)
