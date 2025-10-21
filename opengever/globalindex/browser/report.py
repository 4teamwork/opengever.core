from datetime import datetime
from opengever.base.browser.reporting_view import BaseReporterView
from opengever.base.model import create_session
from opengever.base.reporter import DATE_NUMBER_FORMAT
from opengever.base.reporter import readable_actor
from opengever.base.reporter import StringTranslater
from opengever.base.reporter import XLSReporter
from opengever.base.utils import is_administrator
from opengever.globalindex import _
from opengever.globalindex.utils import get_selected_items
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.group import Group
from opengever.ogds.models.group_membership import GroupMembership
from opengever.ogds.models.service import ogds_service
from opengever.task.helper import task_type_value_helper
from Products.statusmessages.interfaces import IStatusMessage
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import true
from zExceptions import Unauthorized
from zope.i18n import translate


def get_link(value, task):
    return task.absolute_url()


class TaskReporter(BaseReporterView):
    """View that generate an excel spreadsheet which list all selected
    task and their important attributes from the globalindex.
    """

    filename = 'task_report.xlsx'

    @property
    def _columns(self):
        return [
            {'id': 'title', 'title': _('label_title'), 'hyperlink': get_link},
            {'id': 'review_state', 'title': _('review_state'),
             'transform': StringTranslater(
                 self.context.REQUEST, 'plone').translate},
            {'id': 'deadline', 'title': _('label_deadline'),
             'number_format': DATE_NUMBER_FORMAT},
            {'id': 'completed', 'title': _('label_completed'),
             'number_format': DATE_NUMBER_FORMAT},
            {'id': 'containing_dossier', 'title': _('label_dossier')},
            {'id': 'get_main_task_title', 'callable': True,
             'title': _('label_main_task', default=u'Main task')},
            {'id': 'issuer', 'title': _('label_issuer'),
             'transform': readable_actor},
            {'id': 'issuing_org_unit_label',
             'title': _('label_issuing_org_unit')},
            {'id': 'responsible', 'title': _('label_responsible'),
             'transform': readable_actor},
            {'id': 'task_type', 'title': _('label_task_type'),
             'transform': task_type_value_helper},
            {'id': 'admin_unit_id', 'title': _('label_admin_unit_id')},
            {'id': 'sequence_number', 'title': _('label_sequence_number')},
            {'id': 'text', 'title': _('label_description', default=u'Description')},
        ]

    def __call__(self):
        tasks = get_selected_items(self.context, self.request)
        tasks = [tt for tt in tasks]

        if not tasks:
            msg = _(
                u'error_no_items', default=u'You have not selected any items.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            if self.request.get('orig_template'):
                return self.request.RESPONSE.redirect(
                    self.request.form['orig_template'])
            else:
                return self.request.RESPONSE.redirect(
                    self.context.absolute_url())

        reporter = XLSReporter(
            self.context.REQUEST,
            self.columns(),
            tasks,
            sheet_title=translate(
                _('label_tasks', default=u'Tasks'), context=self.request),
            footer='%s %s' % (
                datetime.now().strftime('%d.%m.%Y %H:%M'),
                get_current_admin_unit().id())
        )

        return self.return_excel(reporter)


class UserReport(BaseReporterView):
    """View that generate an excel spreadsheet which list all selected users
    """
    filename = "user_report.xlsx"

    def check_permissions(self):
        if not is_administrator():
            raise Unauthorized

    def extract_user_ids_from_request(self):
        user_ids = self.request.form.get("user_ids")

        if not user_ids:
            msg = _(
                u'error_no_items', default=u'You have not selected any items.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            if self.request.get('orig_template'):
                return self.request.RESPONSE.redirect(
                    self.request.form['orig_template'])
            else:
                return self.request.RESPONSE.redirect(
                    self.context.absolute_url())
        return user_ids

    def fetch_users(self):
        user_ids = self.extract_user_ids_from_request()
        users = [ogds_service().fetch_user(user_id) for user_id in user_ids]
        users = [user for user in users if user]
        return users

    def __call__(self):
        self.check_permissions()
        users = self.fetch_users()
        reporter = XLSReporter(
            self.context.REQUEST,
            self.columns(),
            users,
            sheet_title=translate(
                _('label_users', default=u'Users'), context=self.request)
        )

        return self.return_excel(reporter)

    @property
    def _columns(self):
        columns = [
            {'id': 'username', 'title': _('label_username')},
            {'id': 'active', 'title': _('label_active')},
            {'id': 'firstname', 'title': _('label_firstname')},
            {'id': 'lastname', 'title': _('label_lastname')},
            {'id': 'display_name', 'title': _('label_display_name')},
            {'id': 'directorate', 'title': _('label_directorate')},
            {'id': 'directorate_abbr', 'title': _('label_directorate_abbr')},
            {'id': 'department', 'title': _('label_department')},
            {'id': 'department_abbr', 'title': _('label_department_abbr')},
            {'id': 'organization', 'title': _('label_organization')},
            {'id': 'email', 'title': _('label_email')},
            {'id': 'email2', 'title': _('label_email2')},
            {'id': 'url', 'title': _('label_url')},
            {'id': 'phone_office', 'title': _('label_phone_office')},
            {'id': 'phone_fax', 'title': _('label_phone_fax')},
            {'id': 'phone_mobile', 'title': _('label_phone_mobile')},
            {'id': 'salutation', 'title': _('label_salutation')},
            {'id': 'title', 'title': _('label_title')},
            {'id': 'description', 'title': _('label_description', default=u'Description')},
            {'id': 'address1', 'title': _('label_address1')},
            {'id': 'address2', 'title': _('label_address2')},
            {'id': 'zip_code', 'title': _('label_zip_code')},
            {'id': 'city', 'title': _('label_city')},
            {'id': 'country', 'title': _('label_country')},
            {'id': 'last_login', 'title': _('label_last_login'), 'number_format': DATE_NUMBER_FORMAT},

        ]
        return columns


class OGDSGroupsMembershipReporter(BaseReporterView):
    """API Endpoint that returns all groups with their related users from ogds.

    GET /group-memberships-report HTTP/1.1

    The endpoint returns each group with a list of its associated users.
    """
    filename = 'group-memberships-report.xlsx'

    def check_permissions(self):
        if not is_administrator():
            raise Unauthorized

    @property
    def _columns(self):
        return [
            {'id': 'user_name', 'title': _('label_username')},
            {'id': 'user_fullname', 'title': _('label_fullname')},
            {'id': 'group_title', 'title': _('label_group_title')},
            {'id': 'group_name', 'title': _('label_groupname')},
            {"id": 'membership_note', 'title': _('label_membership_note')},

        ]

    def __call__(self):
        session = create_session()
        query = (
            session.query(Group)
            .options(joinedload(Group.memberships).joinedload(GroupMembership.user))
            .filter(Group.active == true())
        )
        groups_with_users = []

        for group in query.all():
            for membership in group.memberships:
                user = membership.user
                if not user.active:
                    continue
                group_info = {
                    'group_name': group.groupname,
                    'group_title': group.title,
                    'user_name': user.username,
                    'user_fullname': user.fullname(),
                    'membership_note': membership.note or u'',
                }
                groups_with_users.append(group_info)

        reporter = XLSReporter(
            self.context.REQUEST,
            self.columns(),
            groups_with_users,
            sheet_title=translate(
                _('label_groups_membership_report', default=u'Groups membership report'), context=self.request),
            footer='%s %s' % (
                datetime.now().strftime('%d.%m.%Y %H:%M'),
                get_current_admin_unit().id()),
            is_auto_filter_enabled=True
        )
        return self.return_excel(reporter)
