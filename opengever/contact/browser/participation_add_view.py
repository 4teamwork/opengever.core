from opengever.contact import is_contact_feature_enabled
from Products.Five.browser import BrowserView


class ParticipationAddView(BrowserView):
    """A simple redirector view which redirects to the corresponding add form,
    depending on the is_contact_feature_enabled flag.

    The view is called by dossiers `Add participation` factoriesmenu action.
    """

    def __call__(self):
        if is_contact_feature_enabled():
            return self.request.RESPONSE.redirect('add-sql-participation')

        return self.request.response.redirect('add-plone-participation')
