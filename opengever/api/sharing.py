from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services.content.sharing import SharingGet as APISharingGet
from zope.component import queryMultiAdapter


class SharingGet(APISharingGet):
    """Returns a serialized content object.
    """

    def reply(self):
        """Disable `plone.DelegateRoles` permission check.
        """

        serializer = queryMultiAdapter((self.context, self.request),
                                       interface=ISerializeToJson,
                                       name='local_roles')
        if serializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(message='No serializer available.'))

        return serializer(search=self.request.form.get('search'))
