from opengever.base.model import Base
from opengever.base.model import EMAIL_LENGTH
from opengever.base.model import FIRSTNAME_LENGTH
from opengever.base.model import LASTNAME_LENGTH
from opengever.base.model import USER_ID_LENGTH
from opengever.base.query import BaseQuery
from opengever.base.types import UnicodeCoercingText
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import event
from sqlalchemy import func
from sqlalchemy import Index
from sqlalchemy import String


class UserQuery(BaseQuery):

    searchable_fields = ['userid', 'firstname', 'lastname', 'email']

    def get_by_userid(self, userid):
        return self.filter_by(userid=userid).first()


class User(Base):
    """User model
    """

    query_cls = UserQuery

    __tablename__ = 'users'

    userid = Column(String(USER_ID_LENGTH), primary_key=True)
    username = Column(String(USER_ID_LENGTH), nullable=False)
    external_id = Column(String(USER_ID_LENGTH), unique=True, nullable=False)

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
    title = Column(String(255))
    description = Column(UnicodeCoercingText())
    address1 = Column(String(100))
    address2 = Column(String(100))
    zip_code = Column(String(10))
    city = Column(String(100))

    country = Column(String(20))

    last_login = Column(Date, index=True)

    absent = Column(Boolean, default=False)
    absent_from = Column(Date)
    absent_to = Column(Date)

    column_names_to_sync = {
        'userid', 'username', 'external_id', 'active', 'firstname', 'lastname', 'directorate',
        'directorate_abbr', 'department', 'department_abbr', 'email', 'email2',
        'url', 'phone_office', 'phone_fax', 'phone_mobile', 'salutation',
        'title', 'description', 'address1', 'address2', 'zip_code', 'city',
        'country',
    }

    # A classmethod property needs to be defined on the metaclass
    class __metaclass__(type(Base)):
        @property
        def columns_to_sync(cls):
            return {
                col for col in cls.__table__.columns
                if col.name in cls.column_names_to_sync
            }

    def __init__(self, userid, **kwargs):
        self.userid = userid
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return '<User %r>' % self.userid

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

        return u"%s (%s)" % (self.fullname(), self.userid)

    def fullname(self):
        """Return a visual representation of the UserPersona as String.
        - The default is "<lastname> <firstname>"
        - If either one is missing it is: "<lastname>" or "<firstname>"
        - The fallback is "<userid>"
        """
        parts = []
        if self.lastname:
            parts.append(self.lastname)
        if self.firstname:
            parts.append(self.firstname)
        if not parts:
            parts.append(self.userid)

        return u' '.join(parts)


def create_additional_user_indexes(table, connection, *args, **kw):
    engine = connection.engine
    if engine.dialect.name != 'sqlite':
        # SQLite 3.7 (as used on Jenkins) doesn't support the syntax yet
        # that SQLAlchemy produces for this functional index
        ix = Index('ix_users_userid_lower', func.lower(table.c.userid))
        ix.create(engine)


event.listen(User.__table__, 'after_create', create_additional_user_indexes)
