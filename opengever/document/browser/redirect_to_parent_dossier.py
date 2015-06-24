from five import grok
from opengever.document.behaviors import IBaseDocument


class RedirectToParentDossier(grok.View):
    """Redirects to the containing subdossier of a document.
    """
    grok.context(IBaseDocument)
    grok.name('redirect_to_parent_dossier')
    grok.require('zope2.View')

    def render(self):
        dossier = self.context.get_parent_dossier()
        assert dossier, ('the redirect view should only be called when a '
                         'parent dossier is available')

        return self.request.RESPONSE.redirect(dossier.absolute_url())
