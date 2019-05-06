from opengever.dossier import _
from plone import api
from Products.Five.browser import BrowserView


MAIN_DOSSIER_ACTIVE = _("This subdossier can't be activated,"
                        "because the main dossiers is inactive")


class DossierActivator(object):

    def __init__(self, context):
        self.context = context

    def check_preconditions(self):
        errors = []
        if self.context.is_subdossier():
            state = api.content.get_state(self.context.get_parent_dossier())
            if state == 'dossier-state-inactive':
                errors.append(MAIN_DOSSIER_ACTIVE)
        return errors

    def activate(self):
        # subdossiers
        for subdossier in self.context.get_subdossiers():
            subdossier.getObject().activate()

        # main dossier
        self.context.activate()


class DossierActivateView(BrowserView):
    """View which activates the dossier including its subdossiers."""

    def __call__(self):
        activator = DossierActivator(self.context)
        errors = activator.check_preconditions()
        if errors:
            self.show_errors(errors)
            return self.redirect()

        activator.activate()
        api.portal.show_message(_("The Dossier has been activated"),
                                self.request, type='info')
        return self.redirect()

    def show_errors(self, errors):
        for msg in errors:
            api.portal.show_message(
                message=msg, request=self.request, type='error')

    def redirect(self):
        return self.request.RESPONSE.redirect(self.context.absolute_url())
