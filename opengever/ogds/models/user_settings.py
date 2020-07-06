from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.model import USER_ID_LENGTH
from opengever.ogds.models.user import User
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from zope import schema
from zope.interface import Interface
import json


class IUserSettings(Interface):

    notify_own_actions = schema.Bool(required=False, default=False)
    notify_inbox_actions = schema.Bool(required=False, default=True)
    seen_tours = schema.List(value_type=schema.TextLine(),
                             default=[], missing_value=[], required=False)


class UserSettings(Base):

    __tablename__ = 'user_settings'

    userid = Column(String(USER_ID_LENGTH), ForeignKey(User.userid), primary_key=True)
    user = relationship(User, backref=backref("user_settings", uselist=False))

    notify_own_actions = Column(Boolean, default=False, nullable=False)
    notify_inbox_actions = Column(Boolean, default=True, nullable=False)
    _seen_tours = Column(Text, nullable=True)

    @classmethod
    def get_setting_for_user(cls, userid, setting_name):
        setting = cls.query.filter_by(userid=userid).one_or_none()
        return cls.get_setting(setting, setting_name)

    @classmethod
    def get_setting(cls, setting, setting_name):
        if setting is None:
            # User has no personal setting
            if setting_name == 'seen_tours':
                return []
            return getattr(cls, setting_name).default.arg

        # User has a personal setting
        return getattr(setting, setting_name)

    @classmethod
    def save_setting_for_user(cls, userid, setting_name, value):
        """Creates a new entry for the user if necessary and saves the value
        for the given setting.

        Note that seen_tours cannot be set through this method as it is not
        a column in the table. One can set _seen_tours instead, but this
        circumvents the setter, so make sure that the value is not a list but
        a json.dumps of the list.
        """
        # Make sure that setting_name is a column of the UserSettings model.
        error_msg = "{} has to be a column on UserSettings".format(setting_name)
        assert setting_name in cls.__table__.columns, error_msg

        setting = cls.get_or_create(userid)
        setattr(setting, setting_name, value)

    @classmethod
    def get_or_create(cls, userid):
        setting = cls.query.filter_by(userid=userid).one_or_none()
        if setting is None:
            # User has no personal setting
            setting = cls(userid=userid)
            create_session().add(setting)
            setting = cls.query.filter_by(userid=userid).one()

        return setting

    @property
    def seen_tours(self):
        tours = self._seen_tours
        if tours:
            return json.loads(self._seen_tours)

        return []

    @seen_tours.setter
    def seen_tours(self, tours):
        self._seen_tours = json.dumps(tours)
