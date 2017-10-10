from Products.Five import BrowserView


class RedirectToParentDossier(BrowserView):
    """Redirects to the containing subdossier of a document.
    """
    def __call__(self):
        dossier = self.context.get_parent_dossier()
        assert dossier, ('the redirect view should only be called when a '
                         'parent dossier is available')

        return self.request.RESPONSE.redirect(dossier.absolute_url())
