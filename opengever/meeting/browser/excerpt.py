from opengever.base.oguid import Oguid
from opengever.base.security import elevated_privileges
from opengever.base.transport import Transporter
from opengever.document.versioner import Versioner
from opengever.meeting import _
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.i18n import translate
import json


class UpdateDossierExcerpt(BrowserView):
    """Receives a JSON serialized excerpt and updates the excerpt referenced
    by the oguid parameter.

    """

    def __call__(self):
        oguid_str = self.request.get('oguid')
        if not oguid_str:
            raise NotFound()

        oguid = Oguid.parse(oguid_str)

        with elevated_privileges():
            document = oguid.resolve_object()
            if document.is_checked_out():
                raise Unauthorized()

            transporter = Transporter()
            transporter.update(document, self.request)

            comment = translate(
                _(u"Updated with a newer excerpt version."),
                context=self.request)
            Versioner(document).create_version(comment)
        return json.dumps({})
