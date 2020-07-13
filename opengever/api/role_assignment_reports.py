from opengever.base.interfaces import IRoleAssignmentReportsStorage
from plone.app.uuid.utils import uuidToObject
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class RoleAssignmentReportsGet(Service):
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
            reportid = self.params[0]
            try:
                result = storage.get(reportid)
            except KeyError:
                raise BadRequest("Invalid reportid '{}'".format(reportid))
            for item in result['items']:
                item['url'] = uuidToObject(item['UID']).absolute_url()
        # all reports
        elif len(self.params) == 0:
            result = {'items': storage.list()}
            for report in result['items']:
                del report['items']
                report['@id'] = '/'.join([self.context.absolute_url(), '@role-assignment-reports',
                                          report['reportid']])
        else:
            raise BadRequest("Too many parameters. Only principalid is allowed.")

        batch = HypermediaBatch(self.request, result['items'])
        result['items'] = [item for item in batch]
        result['items_total'] = batch.items_total
        result['@id'] = batch.canonical_url
        if batch.links:
            result['batching'] = batch.links
        return result


class RoleAssignmentReportsPost(Service):

    def reply(self):
        self.extract_data()
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        storage = IRoleAssignmentReportsStorage(self.context)
        reportid = storage.add(self.principalid)
        report = storage.get(reportid)
        report['@id'] = '/'.join([self.context.absolute_url(), '@role-assignment-reports',
                                  reportid])
        report['items_total'] = 0
        return report

    def extract_data(self):
        data = json_body(self.request)
        self.principalid = data.get("principalid", None)
        if not self.principalid:
            raise BadRequest("Property 'principalid' is required")


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
            raise BadRequest("reportid is required")
        reportid = self.params[0]
        storage = IRoleAssignmentReportsStorage(self.context)
        try:
            storage.get(reportid)
        except KeyError:
            raise BadRequest("Invalid reportid '{}'".format(reportid))

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        storage = IRoleAssignmentReportsStorage(self.context)
        storage.delete(reportid)
        self.request.response.setStatus(204)
        return super(RoleAssignmentReportsDelete, self).reply()
