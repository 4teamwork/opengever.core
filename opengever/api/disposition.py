from opengever.api import _
from opengever.api.deserializer import GeverDeserializeFromJson
from opengever.api.not_reported_exceptions import BadRequest as NotReportedBadRequest
from opengever.api.relationfield import relationfield_value_to_object
from opengever.api.response import SerializeResponseToJson
from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.utils import unrestrictedUuidToObject
from opengever.disposition.disposition import IDispositionSchema
from opengever.disposition.interfaces import IAppraisal
from opengever.disposition.interfaces import IDisposition
from opengever.disposition.response import IDispositionResponse
from opengever.disposition.validators import OfferedDossiersValidator
from opengever.repository.interfaces import IRepositoryFolder
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.restapi.services.content.update import ContentPatch
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import Invalid


@implementer(IDeserializeFromJson)
@adapter(IDispositionSchema, Interface)
class DeserializeDispositionFromJson(GeverDeserializeFromJson):
    """In order to be able to return translated and speaking error
    messages, we have to manually check the dossier data and raise any errors.
    """

    def __call__(self, validate_all=False, data=None, create=False):
        if data is None:
            data = json_body(self.request)

        # Pre validate selected dossiers to provide specific error message
        # if invalid
        dossiers = []
        field = IDispositionSchema['dossiers']
        for value in data.get('dossiers', []):
            obj, resolved_by = relationfield_value_to_object(
                value, self.context, self.request)
            dossiers.append(obj)

            try:
                validator = OfferedDossiersValidator(
                    self.context, self.request, None, field, None)
                validator.validate(dossiers)
            except Invalid as err:
                raise BadRequest(err.message)

        return super(DeserializeDispositionFromJson, self).__call__(
            validate_all=validate_all, data=data, create=create)


@implementer(ISerializeToJson)
@adapter(IDispositionSchema, Interface)
class SerializeDispositionToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeDispositionToJson, self).__call__(*args, **kwargs)
        result[u'sip_filename'] = self.context.get_sip_filename()
        result[u'sip_delivery_status'] = self.context.get_delivery_status_infos()
        result[u'dossier_details'] = self.get_dossier_details()
        result[u'has_dossiers_with_pending_permissions_changes'] = self.context.has_dossiers_with_pending_permissions_changes
        return result

    def get_dossier_details(self):
        active_dossiers, inactive_dossiers = \
            self.context.get_grouped_dossier_representations()

        data = {
            'active_dossiers': self.jsonify(active_dossiers),
            'inactive_dossiers': self.jsonify(inactive_dossiers),
        }
        return data

    def jsonify(self, data):
        compatible_data = []
        for repo, dossiers in data:
            repo_data = self.repo_serialization(repo)
            repo_data['dossiers'] = [
                dossier.jsonify() for dossier in dossiers]

            compatible_data.append(repo_data)

        return compatible_data

    def repo_serialization(self, repo):
        if IRepositoryFolder.providedBy(repo):
            repo_data = queryMultiAdapter(
                (repo, getRequest()), ISerializeToJsonSummary)()
            repo_data['archival_value'] = self.repo_archival_value(repo)
            return repo_data

        # In a closed disposition
        return {'title': repo}

    def repo_archival_value(self, repo):
        return getMultiAdapter(
            (ILifeCycle['archival_value'], repo, getRequest()),
            IFieldSerializer)()


class AppraisalPatch(Service):

    def reply(self):
        data = json_body(self.request)
        appraisal = IAppraisal(self.context)

        disposition_dossiers = self.context.get_dossiers()
        for uid, archive in data.items():
            dossier = unrestrictedUuidToObject(uid)
            if not dossier or dossier not in disposition_dossiers:
                msg = _(
                    u'msg_invalid_uid',
                    default=u'Dossier with the UID ${uid} is not part of the disposition',
                    mapping={'uid': uid})
                raise BadRequest(msg)

            appraisal.update(dossier=dossier, archive=archive)

        prefer = self.request.getHeader("Prefer")
        if prefer == "return=representation":
            self.request.response.setStatus(200)
            serializer = queryMultiAdapter(
                (self.context, self.request), ISerializeToJson)
            return serializer()

        return self.reply_no_content()


class TransferNumberPatch(ContentPatch):

    def reply(self):
        data = json_body(self.request)
        if 'transfer_number' not in data:
            raise NotReportedBadRequest(_(
                u'transfer_number_required',
                default=u"Property 'transfer_number' is required."))
        transfer_number = data['transfer_number']
        IDisposition(self.context).transfer_number = transfer_number
        return super(TransferNumberPatch, self).reply()


@implementer(ISerializeToJson)
@adapter(IDispositionResponse, Interface)
class SerializeDispositionResponseToJson(SerializeResponseToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeDispositionResponseToJson, self).__call__(
            *args, **kwargs)

        result['dossiers'] = json_compatible(self.context.dossiers)
        return result
