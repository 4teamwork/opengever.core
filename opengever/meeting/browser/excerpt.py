from five import grok
from opengever.base.oguid import Oguid
from opengever.base.security import elevated_privileges
from opengever.base.transport import Transporter
from opengever.meeting import _
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.i18n import translate
import json


class UpdateDossierExcerpt(grok.View):
    """Receives a JSON serialized excerpt and updates the excerpt referenced
    by the oguid parameter.

    """
    grok.name('update-dossier-excerpt')
    grok.require('zope2.View')
    grok.context(IPloneSiteRoot)

    def render(self):
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

            repository = api.portal.get_tool('portal_repository')
            comment = translate(
                _(u"Updated with a newer excerpt version."),
                context=self.request)
            repository.save(obj=document, comment=comment)
        return json.dumps({})
