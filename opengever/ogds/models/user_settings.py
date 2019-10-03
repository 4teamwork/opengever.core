from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.model import USER_ID_LENGTH
from opengever.ogds.models.user import User
from plone import api
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship


class UserSettings(Base):

    __tablename__ = 'user_settings'

    userid = Column(String(USER_ID_LENGTH), ForeignKey(User.userid), primary_key=True)
    user = relationship(User, backref="user_settings")

    notify_own_actions = Column(Boolean, default=False, nullable=False)
    notify_inbox_actions = Column(Boolean, default=True, nullable=False)
    _seen_tours = Column(Text, nullable=True)

    @classmethod
    def get_setting_for_user(cls, userid, setting_name):
        config = cls.query.filter_by(userid=userid).one_or_none()
        if config is None:
            # User has no personal setting
            return getattr(cls, setting_name).default.arg
        # User has a personal setting
        return getattr(config, setting_name)

    @classmethod
    def save_setting_for_user(cls, userid, setting_name, value):
        # Make sure that setting_name is a column of the UserSettings model.
        error_msg = "{} has to be a column on UserSettings".format(setting_name)
        assert setting_name in cls.__table__.columns, error_msg

        config = cls.query.filter_by(userid=userid).one_or_none()
        if config is None:
            # User has no personal setting
            config = cls(userid=userid)
            create_session().add(config)
        setattr(config, setting_name, value)

    @property
    def seen_tours(self):
        tours = self._seen_tours
        if tours:
            return json.loads(self._seen_tours)

        return []

    @seen_tours.setter
    def seen_tours(self, tours):
        self._seen_tours = json.dumps(tours)
