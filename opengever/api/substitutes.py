from opengever.api.batch import SQLHypermediaBatch
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.ogds.base.substitute import SubstituteManager
from opengever.ogds.models.substitute import Substitute
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from opengever.api.serializer import SerializeSQLModelToJsonBase


@implementer(ISerializeToJson)
@adapter(Substitute, IOpengeverBaseLayer)
class SerializeSubstituteToJson(SerializeSQLModelToJsonBase):

    content_type = 'virtual.ogds.substitute'

    def __call__(self):
        data = super(SerializeSubstituteToJson, self).__call__()
        if '@substitutes' in self.request.URL:
            data['@id'] = '{}/@substitutes/{}/{}'.format(
                api.portal.get().absolute_url(),
                self.context.userid,
                self.context.substitute_userid)
        else:
            data['@id'] = '{}/@my-substitutes/{}'.format(
                api.portal.get().absolute_url(),
                self.context.substitute_userid)

        return data


class MySubstitutesGet(Service):

    def reply(self):
        userid = self.get_userid()
        results = SubstituteManager().list_substitutes_for(userid)
        batch = SQLHypermediaBatch(self.request, results, 'substitute_userid')

        serialized_terms = []
        for substitute in batch:
            serializer = getMultiAdapter(
                (substitute, self.request), interface=ISerializeToJson
            )
            serialized_terms.append(serializer())

        result = {
            "@id": batch.canonical_url,
            "items": serialized_terms,
            "items_total": batch.items_total,
        }
        links = batch.links
        if links:
            result["batching"] = links
        return result

    def get_userid(self):
        return api.user.get_current().getId()


class SubstitutesGet(MySubstitutesGet):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(SubstitutesGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def get_userid(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply userid as path parameter.")
        return self.params[0]


class MySubstitutesPost(Service):

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        substitute = json_body(self.request).get("userid", None)
        if not substitute:
            raise BadRequest("Property 'userid' is required")
        if not api.user.get(substitute):
            raise BadRequest("userid '{}' does not exist".format(substitute))
        userid = api.user.get_current().getId()
        SubstituteManager().add(userid, substitute)
        return self.reply_no_content()


class MySubstitutesDelete(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(MySubstitutesDelete, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def reply(self):
        substitute = self.read_params()
        userid = api.user.get_current().getId()
        SubstituteManager().delete(userid, substitute)
        return self.reply_no_content()

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply substitute userid as path parameter.")
        return self.params[0]
