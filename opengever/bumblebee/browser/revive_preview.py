from ftw.bumblebee.interfaces import IBumblebeeable
from ftw.bumblebee.interfaces import IBumblebeeDocument
from opengever.bumblebee import _
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.document.versioner import Versioner
from plone import api
from plone.restapi.deserializer import json_body
from Products.Five import BrowserView


class RevivePreview(BrowserView):
    """Sometimes creating a bumblebee preview fails and in rare circumstances
    this leaves bumblebee in an inconsistent state (GEVER-side).

    It also may happen that the bumblebee service is down temporarily and the
    documents can't be registered.

    These documents won't show a preview until the document is modified and
    thus triggers a bumblebee update.

    This view lets you fix this inconsistent bumblebee document either through
    calling the view directly in the browser with

    @@revive_preview

    or you use the action on the object to revive the current object.
    """
    def __call__(self):
        """Handles the reviving process.
        """
        if self.available():

            data = json_body(self.request)
            version = data.get('version')
            if version and version != 'current':
                document = Versioner(self.context).retrieve(version)
            else:
                document = self.context
            # Indicates that this context should not be converted if the
            # checksum didn't change. Even the force attribute respects this
            # marker-attribute.
            #
            # Because we really want to update the document, we just remove
            # this property.
            if hasattr(document, '_v_bumblebee_last_converted'):
                delattr(document, '_v_bumblebee_last_converted')

            # Forces a document-update. Means, regenerating the checksum
            # and queue storing in bumblebee.
            IBumblebeeDocument(document)._handle_update(force=True)

            api.portal.show_message(message=_(u'preview_revived',
                                              default=u'Preview revived and will be available soon'),
                                    request=self.request, type='info')
        else:
            api.portal.show_message(message=_(u'preview_revive_not_available',
                                              default=u'Reviving the preview is not available for this context.'),
                                    request=self.request, type='error')

        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def available(self):
        """Checks if reviving is available for the current object
        """
        if not is_bumblebee_feature_enabled():
            return False

        if not IBumblebeeable.providedBy(self.context):
            return False

        return True
