from datetime import date
from opengever.base.security import elevated_privileges
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier
from plone import api
from Products.Five.browser import BrowserView


class DossierDeactivateView(BrowserView):
    """Recursively deactivate the dossier and its subdossiers.

    Preconditions:
    * All contained documents are checked in.
    * Some subdossiers are already resolved.
    * Some subdossiers cannot be deactivated by the user.
    * The user has no access to some of the subdossiers.
    * The dossier contains active tasks.
    """

    def __call__(self):
        if not self.check_preconditions():
            return self.redirect()

        # recursively deactivate all dossiers
        for subdossier in self.context.get_subdossiers():
            state = api.content.get_state(obj=subdossier.getObject())
            if state != 'dossier-state-inactive':
                api.content.transition(
                    obj=subdossier.getObject(),
                    transition=u'dossier-transition-deactivate')

        # deactivate main dossier
        self.set_end_date(self.context)
        api.content.transition(obj=self.context,
                               transition='dossier-transition-deactivate')

        api.portal.show_message(
            _("The Dossier has been deactivated"), self.request, type='info')

        return self.redirect()

    def set_end_date(self, dossier):
        if not IDossier(dossier).end:
            IDossier(dossier).end = date.today()

    def redirect(self):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def check_preconditions(self):
        satisfied = True

        if not self.context.is_all_checked_in():
            api.portal.show_message(
                _(u"The Dossier can't be deactivated, not all contained"
                  "documents are checked in."), self.request, type='error')
            satisfied = False

        if self.context.has_active_proposals():
            api.portal.show_message(
                _(u"The Dossier can't be deactivated, it contains active "
                  "proposals."), self.request, type='error')
            satisfied = False

        # Check for subdossiers the user cannot deactivate
        for subdossier in self.context.get_subdossiers(unrestricted=True):
            with elevated_privileges():
                subdossier = subdossier.getObject()

            wftool = api.portal.get_tool('portal_workflow')
            user_can_deactivate = any(
                transition['name'] == 'dossier-transition-deactivate'
                for transition in wftool.getTransitionsFor(subdossier)
            )
            state = api.content.get_state(subdossier)

            # A subdossier already being inactive is not a blocker
            if not user_can_deactivate and state != 'dossier-state-inactive':
                if api.user.has_permission('View', obj=subdossier):
                    subdossier_title = subdossier.title_or_id()
                    # We cannot deactivate if some of the subdossiers are already resolved
                    if state == 'dossier-state-resolved':
                        msg = _(
                            u"The Dossier can't be deactivated, the subdossier ${dossier} is already resolved.",
                            mapping=dict(dossier=subdossier_title),
                        )
                    else:
                        # The deactvation of this subdossier is most likely not allowed by role
                        msg = _(
                            u"The Dossier ${dossier} can't be deactivated by the user.",
                            mapping=dict(dossier=subdossier_title),
                        )
                # Inform the user which of the parents contains the blocking subdossier they cannot see
                else:
                    # We are guaranteed to hit a dossier the user can view
                    parent_title = ''
                    parents = [subdossier.get_parent_dossier()]

                    # Traverse up the parents until we hit a non-dossier
                    while parents[-1].get_parent_dossier():
                        parents.append(parents[-1].get_parent_dossier())

                    # Grab the title of the first parent we do have access to
                    for parent in parents:
                        if api.user.has_permission('View', obj=parent):
                            parent_title = parent.title_or_id()
                            break

                    msg = _(
                        u"The Dossier ${dossier} contains a subdossier which can't be deactivated by the user.",
                        mapping=dict(dossier=parent_title),
                    )

                api.portal.show_message(msg, self.request, type='error')
                satisfied = False

        if self.context.has_active_tasks():
            satisfied = False
            api.portal.show_message(
                _(u"The Dossier can't be deactivated, not all contained "
                  "tasks are in a closed state."),
                self.request, type='error')

        return satisfied
