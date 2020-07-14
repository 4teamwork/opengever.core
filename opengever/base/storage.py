from copy import deepcopy
from DateTime import DateTime
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.interfaces import IRoleAssignmentReportsStorage
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.actor import OGDSGroupActor
from opengever.ogds.base.actor import OGDSUserActor
from opengever.ogds.base.actor import PloneUserActor
from persistent.mapping import PersistentMapping
from plone.restapi.serializer.converters import json_compatible
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.interface import implementer

PRINCIPAL_TYPE_GROUP = 'group'
PRINCIPAL_TYPE_UNKNOWN = 'unknown principal'
PRINCIPAL_TYPE_USER = 'user'
STATE_IN_PROGRESS = 'in progress'
STATE_READY = 'ready'


@implementer(IRoleAssignmentReportsStorage)
@adapter(IPloneSiteRoot)
class RoleAssignmentReportsStorage(object):
    """Default IRoleAssignmentReportsStorage implementation.

    Stores role assignment reports in annotations on the Plone site. See interface for
    detailed documentation.
    """

    ANNOTATIONS_KEY = 'opengever.base.role_assignment_reports'
    STORAGE_REPORTS_KEY = 'reports'
    STORAGE_NEXT_ID_KEY = 'next_id'

    def __init__(self, context):
        self.context = context

        self._storage = None
        self.initialize_storage()

    def initialize_storage(self):
        annotations = IAnnotations(self.context)
        if self.ANNOTATIONS_KEY not in annotations:
            annotations[self.ANNOTATIONS_KEY] = PersistentMapping()

        self._storage = annotations[self.ANNOTATIONS_KEY]

        if self.STORAGE_REPORTS_KEY not in self._storage:
            self._storage[self.STORAGE_REPORTS_KEY] = PersistentMapping()
        self._reports = self._storage[self.STORAGE_REPORTS_KEY]

        # Counter for the next 'report_id'
        if self.STORAGE_NEXT_ID_KEY not in self._storage:
            self._storage[self.STORAGE_NEXT_ID_KEY] = 0

    @staticmethod
    def _get_principal_type(principalid):
        principal = ActorLookup(principalid).lookup()
        if isinstance(principal, (OGDSUserActor, PloneUserActor)):
            return PRINCIPAL_TYPE_USER
        elif isinstance(principal, OGDSGroupActor):
            return PRINCIPAL_TYPE_GROUP
        else:
            return PRINCIPAL_TYPE_UNKNOWN

    def add(self, principalid):
        report_id = self._generate_report_id()
        self._reports[report_id] = PersistentMapping({
            'items': [],
            'modified': json_compatible(utcnow_tz_aware()),
            'principalid': principalid,
            'principal_type': self._get_principal_type(principalid),
            'reportid': report_id,
            'state': STATE_IN_PROGRESS
        })
        return report_id

    def update(self, report_id, report_data):
        self._reports[report_id].update(report_data)
        self._reports[report_id]['modified'] = json_compatible(utcnow_tz_aware())

    @staticmethod
    def _copy_report(report):
        return deepcopy(dict(report))

    def get(self, report_id):
        # get copy of a report
        return self._copy_report(self._reports[report_id])

    def list(self):
        reports = [self._copy_report(report) for report in self._reports.values()]
        return sorted(reports, key=lambda k: DateTime(k['modified']), reverse=True)

    def delete(self, report_id):
        del self._reports[report_id]

    def _generate_report_id(self):
        new_id = self._storage[self.STORAGE_NEXT_ID_KEY]
        self._storage[self.STORAGE_NEXT_ID_KEY] += 1
        return 'report_' + str(new_id)
