from opengever.base.interfaces import IRoleAssignmentReportsStorage
from opengever.ogds.base.actor import Actor
from opengever.sharing.browser.sharing import GEVER_ROLE_MAPPING
from opengever.sharing.browser.sharing import WORKSPACE_ROLE_MAPPING
from opengever.workspace import is_workspace_feature_enabled
from plone.app.uuid.utils import uuidToObject
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


ROLE_ASSIGNMENT_REPORT_TYPE = 'virtual.report.roleassignmentreport'


class RoleAssignmentReportsBase(Service):

    def add_additional_data_to_report(self, report):
        report['@type'] = ROLE_ASSIGNMENT_REPORT_TYPE
        report['principal_label'] = Actor.lookup(report['principal_id']).get_label()
        report['@id'] = '/'.join([self.context.absolute_url(), '@role-assignment-reports',
                                  report['report_id']])


class RoleAssignmentReportsGet(RoleAssignmentReportsBase):
    """API Endpoint which returns a list of all role assignment reports

    GET /@role-assignment-reports HTTP/1.1

    or a single report

    GET /@role-assignment-reports/report_1 HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(RoleAssignmentReportsGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@role-assignment-reports as parameters
        self.params.append(name)
        return self

    def reply(self):
        storage = IRoleAssignmentReportsStorage(self.context)
        # a single report
        if len(self.params) == 1:
            report_id = self.params[0]
            try:
                result = storage.get(report_id)
            except KeyError:
                raise BadRequest("Invalid report_id '{}'".format(report_id))
            for item in result['items']:
                obj = uuidToObject(item['UID'])
                item['title'] = obj.Title()
                item['url'] = obj.absolute_url()

            result['referenced_roles'] = self.get_referenced_roles()
            self.add_additional_data_to_report(result)
        # all reports
        elif len(self.params) == 0:
            result = {'items': storage.list()}
            for report in result['items']:
                del report['items']
                self.add_additional_data_to_report(report)
        else:
            raise BadRequest("Too many parameters. Only principal_id is allowed.")

        batch = HypermediaBatch(self.request, result['items'])
        result['items'] = [item for item in batch]
        result['items_total'] = batch.items_total
        result['@id'] = batch.canonical_url
        if batch.links:
            result['batching'] = batch.links

        return result

    def get_referenced_roles(self):
        roles = []
        role_mapping = WORKSPACE_ROLE_MAPPING if is_workspace_feature_enabled() else GEVER_ROLE_MAPPING
        for role, title in role_mapping.items():
            roles.append(
                {'id': role,
                 'title': translate(title, context=self.request)})

        return roles


class RoleAssignmentReportsPost(RoleAssignmentReportsBase):

    def reply(self):
        self.extract_data()
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        storage = IRoleAssignmentReportsStorage(self.context)
        report_id = storage.add(self.principal_id)
        report = storage.get(report_id)
        self.add_additional_data_to_report(report)
        report['items_total'] = 0
        return report

    def extract_data(self):
        data = json_body(self.request)
        self.principal_id = data.get("principal_id", None)
        if isinstance(self.principal_id, dict):
            self.principal_id = self.principal_id['token']

        if not self.principal_id:
            raise BadRequest("Property 'principal_id' is required")
        self.principal_id = self.principal_id.split('group:', 1)[-1]


class RoleAssignmentReportsDelete(Service):
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(RoleAssignmentReportsDelete, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@favorites as parameters
        self.params.append(name)
        return self

    def reply(self):
        if len(self.params) != 1:
            raise BadRequest("report_id is required")
        report_id = self.params[0]
        storage = IRoleAssignmentReportsStorage(self.context)
        try:
            storage.get(report_id)
        except KeyError:
            raise BadRequest("Invalid report_id '{}'".format(report_id))

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        storage = IRoleAssignmentReportsStorage(self.context)
        storage.delete(report_id)
        self.request.response.setStatus(204)
        return super(RoleAssignmentReportsDelete, self).reply()
