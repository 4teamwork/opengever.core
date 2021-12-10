from datetime import datetime
from opengever.base.model import Base
from opengever.base.model import USER_ID_LENGTH
from opengever.base.query import BaseQuery
from opengever.ogds.models.user import User
from sqlalchemy import and_
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import or_
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class SubstituteQuery(BaseQuery):

    searchable_fields = ['userid', 'substitute_userid']

    def by_userid(self, userid):
        return self.filter_by(userid=userid)

    def by_userid_and_substitute_userid(self, userid, substitute_userid):
        return self.filter_by(userid=userid, substitute_userid=substitute_userid)

    def by_substitute_userid(self, userid):
        return self.filter_by(substitute_userid=userid)

    def by_absent_users(self):
        today = datetime.now().strftime('%Y-%m-%d')
        return self.filter(or_(
            Substitute.user.has(User.absent == True),  # noqa
            and_(Substitute.user.has(User.absent_from <= today),
                 Substitute.user.has(User.absent_to >= today))))


class Substitute(Base):
    """Substitute model
    """

    query_cls = SubstituteQuery

    __tablename__ = 'substitutes'

    substitution_id = Column("id", Integer, Sequence("substitution_id_seq"), primary_key=True)
    userid = Column(String(USER_ID_LENGTH), ForeignKey(User.userid))
    substitute_userid = Column(String(USER_ID_LENGTH), ForeignKey(User.userid))

    user = relationship("User", foreign_keys=[userid])
    substitute = relationship("User", foreign_keys=[substitute_userid])
