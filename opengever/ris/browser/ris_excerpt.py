from Acquisition import aq_inContextOf
from Acquisition import aq_inner
from opengever.base.interfaces import IDataCollector
from opengever.base.json_response import JSONResponse
from opengever.base.security import elevated_privileges
from opengever.base.transport import PrivilegedReceiveObject
from opengever.base.transport import Transporter
from opengever.document.versioner import Versioner
from opengever.journal.handlers import journal_entry_factory
from opengever.ogds.base.utils import encode_after_json
from opengever.ris import _
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from z3c.relationfield.relation import RelationValue
from zExceptions import BadRequest
from zope.component import getAdapters
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.intid.interfaces import IIntIds
import json


class RISReturnExcerptService(Service):

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        if not api.user.has_permission("View", obj=self.context):
            return JSONResponse(self.request).error("Forbidden", status=403).dump()

        data = json_body(self.request) or {}
        target_cid = data.get("target_admin_unit_id")
        container_path = data.get("target_dossier_relative_path")
        proposal_relative_path = data.get("proposal_relative_path")

        if not target_cid or not container_path:
            return (
                JSONResponse(self.request)
                .error(
                    "Target admin_unit_id and dossier_url are required.",
                    status=400,
                )
                .dump()
            )

        container_path = container_path.lstrip("/")

        result = Transporter().transport_to(
            obj=self.context,
            target_cid=target_cid,
            container_path=container_path,
            view="receive-ris-return-excerpt",
            proposal_relative_path=proposal_relative_path,
            finalize=data.get("finalize", True),
        )
        return result


class RISUpdateExcerptService(Service):

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        if not api.user.has_permission("View", obj=self.context):
            return JSONResponse(self.request).error("Forbidden", status=403).dump()

        data = json_body(self.request) or {}
        target_cid = data.get("target_admin_unit_id")
        container_path = data.get("target_doc_relative_path")

        if not target_cid or not container_path:
            return (
                JSONResponse(self.request)
                .error(
                    "Target admin_unit_id and paths are required.",
                    status=400,
                )
                .dump()
            )

        container_path = container_path.lstrip("/")

        result = Transporter().transport_to(
            obj=self.context,
            target_cid=target_cid,
            container_path=container_path,
            view="receive-ris-update-excerpt",
        )
        return result


class RISReturnExcerptReceive(PrivilegedReceiveObject):
    """Receiver on the target dossier. Runs with elevated privileges."""

    def __call__(self):
        obj = self.receive()
        portal = self.context.portal_url.getPortalObject()
        portal_path = "/".join(portal.getPhysicalPath())

        intids = getUtility(IIntIds)

        data = {
            "path": "/".join(obj.getPhysicalPath())[len(portal_path) + 1:],
            "intid": intids.queryId(obj),
            "url": obj.absolute_url(),
            "current_version_id": obj.get_current_version_id(missing_as_zero=True),
        }

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(data)

    @property
    def container(self):
        return self.context

    def _traverse_relpath(self, relpath):
        portal = api.portal.get()

        rel = (relpath or "").lstrip("/")

        if isinstance(rel, unicode):
            rel = rel.encode("utf-8")
        try:
            return portal.unrestrictedTraverse(rel, default=None)
        except Exception:
            return None

    def _is_within(self, container, obj):
        return aq_inContextOf(aq_inner(obj), aq_inner(container))

    def _link_as_excerpt(self, proposal, document):

        if not hasattr(proposal, "excerpts"):
            raise BadRequest("Proposal has no 'excerpts' field.")

        proposal.excerpts = [RelationValue(getUtility(IIntIds).getId(document))]
        proposal.reindexObject(idxs=["excerpts"])

    def receive(self):
        data = self.request.form or {}
        proposal_path = data.get("proposal_relative_path")
        finalize = data.get("finalize", True)

        document = super(RISReturnExcerptReceive, self).receive()

        if proposal_path:
            proposal = self._traverse_relpath(proposal_path)

            if proposal is None:
                raise BadRequest("Invalid 'proposal_relative_path' (object not found).")

            if not self._is_within(self.container, proposal):
                raise BadRequest("The proposal is not located in the target dossier.")

            self._link_as_excerpt(proposal, document)

        if finalize:
            try:
                with elevated_privileges():
                    api.content.transition(
                        obj=document, transition="document-transition-finalize"
                    )
            except Exception:
                pass

        return document


class RISUpdateExcerptReceive(RISReturnExcerptReceive):
    """Receiver on the target dossier. Runs with elevated privileges."""

    def _apply_payload_as_new_version(self, gever_doc, payload):
        Versioner(gever_doc).create_initial_version()

        data = encode_after_json(payload)

        for name, collector in getAdapters((gever_doc,), IDataCollector):
            if name in data:
                collector.insert(data[name])

        file = data["field-data"]["IDocumentSchema"].get("file")
        if file:
            gever_doc.update_file(
                file["data"],
                content_type=file.get("content-type"),
                filename=file.get("filename"),
                create_version=True,
            )

            journal_entry_factory(
                context=gever_doc,
                action="Update proposal excerpt from SPV",
                title=_("excerpt_was_replaced", default="Excerpt was replaced"),
            )
        api.content.transition(obj=gever_doc, transition="document-transition-finalize")

        return gever_doc

    def receive(self):
        document = self.container
        transporter = Transporter()
        payload = transporter._extract_data(self.request)

        if document is None:
            raise BadRequest("Invalid 'doc_relative_path' (object not found).")

        try:
            with elevated_privileges():
                if document.is_final_document():
                    api.content.transition(
                        obj=document, transition="document-transition-reopen"
                    )

                document = self._apply_payload_as_new_version(document, payload)

        except Exception:
            pass

        return document
