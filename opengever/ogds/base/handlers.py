from DateTime import DateTime
from opengever.ogds.models.user import User


def user_logged_in(event):
    ogds_user = User.query.get_by_userid(event.object.getId())
    if ogds_user:
        login_time = event.object.getProperty('login_time')
        if isinstance(login_time, DateTime):
            ogds_user.last_login = login_time.asdatetime().date()
