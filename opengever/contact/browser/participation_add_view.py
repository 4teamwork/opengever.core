from opengever.contact import _ as contact_mf
from opengever.kub import is_kub_feature_enabled
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage


class ParticipationAddView(BrowserView):
    """A simple redirector view which redirects to the corresponding add form,
    depending on whether KuB is enabled or not.

    The view is called by dossiers `Add participation` factoriesmenu action.
    """

    def __call__(self):
        if is_kub_feature_enabled():
            msg = contact_mf(
                u'warning_kub_contact_new_ui_only',
                default=u'Kub contacts are only supported in the new frontend')
            IStatusMessage(self.request).addStatusMessage(msg, type=u'error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())
        return self.request.response.redirect(
            self.get_url('add-plone-participation'))

    def get_url(self, action):
        return u"{}/{}".format(self.context.absolute_url(), action)
