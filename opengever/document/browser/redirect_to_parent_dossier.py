from Products.Five import BrowserView


class RedirectToParentDossier(BrowserView):
    """Redirects to the containing subdossier of a document.

    Caution: this view will be used by GEVER-UI/RIS/VM
    """
    def __call__(self):
        dossier = self.context.get_parent_dossier()
        assert dossier, ('the redirect view should only be called when a '
                         'parent dossier is available')

        url_parts = [dossier.absolute_url()]
        qs = self.request['QUERY_STRING']
        if qs:
            url_parts.append(qs)
        redirect_url = '?'.join(url_parts)

        return self.request.RESPONSE.redirect(redirect_url)
