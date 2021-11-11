# -*- coding: utf-8 -*-
from opengever.api import _
from opengever.dossier.behaviors.protect_dossier import IProtectDossier
from opengever.dossier.behaviors.protect_dossier import IProtectDossierMarker
from plone.restapi.deserializer import json_body
from plone.restapi.services.content.update import ContentPatch
from zExceptions import Forbidden
from zope.schema import getFieldNames


class GeverContentPatch(ContentPatch):
    """Gever specific implementation to handle dossier protection
    """
    def reply(self):
        result = super(GeverContentPatch, self).reply()

        if self.request.response.status == 403 and \
           result.get('error', {}).get('message') == u'Resource is locked.':
            # Check if its a locked error and raise Forbiden instead of
            # setting the status directly. So we can return a translated
            # error message.
            raise Forbidden(
                _(u'msg_resource_locked', default=u'Resource is locked.'))

        if IProtectDossierMarker.providedBy(self.context):
            protect_fields = getFieldNames(IProtectDossier)
            updated_fields = json_body(self.request).keys()
            protect_fields_changed = set(protect_fields).intersection(set(updated_fields))
            if protect_fields_changed:
                IProtectDossier(self.context).protect()

        return result
