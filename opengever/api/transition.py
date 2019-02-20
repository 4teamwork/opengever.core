from opengever.base.transition import ITransitionExtender
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.services.workflow.transition import WorkflowTransition
from Products.CMFCore.interfaces import IFolderish
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest


class GEVERWorkflowTransition(WorkflowTransition):

    def recurse_transition(self, objs, comment, publication_dates,
                           include_children=False):

        data = json_body(self.request)

        for obj in objs:
            if publication_dates:
                deserializer = queryMultiAdapter((obj, self.request),
                                                 IDeserializeFromJson)
                deserializer(data=publication_dates)

            adapter = queryMultiAdapter(
                (obj, getRequest()), ITransitionExtender, name=self.transition)
            if adapter:
                errors = adapter.validate_schema(data)
                if errors:
                    raise BadRequest(errors)

            self.wftool.doActionFor(obj, self.transition,
                                    comment=comment, transition_params=data)
            if include_children and IFolderish.providedBy(obj):
                self.recurse_transition(
                    obj.objectValues(), comment, publication_dates,
                    include_children)
