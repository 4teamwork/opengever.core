from opengever.ogds.models.service import ogds_service


CACHE = {}


def userid_to_email(userid):
    userid_email_mapping = CACHE.get('userid_email_mapping', None)
    if userid_email_mapping is None:
        users = ogds_service().all_users()
        userid_email_mapping = {user.userid: user.email for user in users}
        CACHE['userid_email_mapping'] = userid_email_mapping
    return userid_email_mapping.get(userid, userid)
