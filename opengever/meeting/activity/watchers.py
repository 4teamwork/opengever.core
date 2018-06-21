from opengever.activity import notification_center
from opengever.activity.roles import COMMITTEE_RESPONSIBLE_ROLE
from opengever.activity.roles import PROPOSAL_ISSUER_ROLE
from opengever.meeting.activity.helpers import get_users_by_group


def add_watchers_on_submitted_proposal_created(obj):
    groupid = obj.load_model().committee.group_id
    for user in get_users_by_group(groupid) or []:
        notification_center().add_watcher_to_resource(
            obj, user.id, COMMITTEE_RESPONSIBLE_ROLE)


def remove_watchers_on_submitted_proposal_deleted(obj, groupid):
    for user in get_users_by_group(groupid) or []:
        notification_center().remove_watcher_from_resource(
            obj, user.id, COMMITTEE_RESPONSIBLE_ROLE)


def add_watcher_on_proposal_created(obj):
    notification_center().add_watcher_to_resource(
        obj, obj.issuer, PROPOSAL_ISSUER_ROLE)


def change_watcher_on_proposal_edited(obj, new_userid):
    center = notification_center()
    center.remove_watcher_from_resource(
        obj, obj.issuer, PROPOSAL_ISSUER_ROLE)
    center.add_watcher_to_resource(
        obj, new_userid, PROPOSAL_ISSUER_ROLE)
