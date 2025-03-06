from opengever.ogds.models.service import ogds_service


CACHE = {}


def userid_to_email(userid):
    userid_email_mapping = CACHE.get('userid_email_mapping', None)
    if userid_email_mapping is None:
        users = ogds_service().all_users()
        userid_email_mapping = {}
        for user in users:
            if user.email:
                userid_email_mapping[user.userid] = user.email
                if user.userid != user.username:
                    userid_email_mapping[user.username] = user.email
        CACHE['userid_email_mapping'] = userid_email_mapping
    return userid_email_mapping.get(userid, userid)
