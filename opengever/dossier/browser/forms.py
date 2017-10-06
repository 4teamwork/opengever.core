from AccessControl import getSecurityManager
from opengever.base.behaviors.utils import hide_fields_from_behavior
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossierMarker
from plone.dexterity.browser import add
from plone.dexterity.i18n import MessageFactory as pd_mf  # noqa
from plone.dexterity.interfaces import IDexterityFTI
from zExceptions import Unauthorized
from zope.component import getUtility


# TODO: temporary default value (autocompletewidget)
class DossierAddForm(add.DefaultAddForm):

    def render(self):
        fti = getUtility(IDexterityFTI, name=self.portal_type)
        if fti not in self.context.allowedContentTypes():
            raise Unauthorized

        return super(DossierAddForm, self).render()

    def update(self):
        """Adds a default value for `responsible` to the request so the
        field is prefilled with the current user, or the parent dossier's
        responsible in the case of a subdossier.
        """
        responsible = getSecurityManager().getUser().getId()

        if not self.request.get('form.widgets.IDossier.responsible', None):
            self.request.set('form.widgets.IDossier.responsible',
                             [responsible])
        super(DossierAddForm, self).update()

    def updateFields(self):
        super(DossierAddForm, self).updateFields()
        hide_fields_from_behavior(self,
                                  ['IClassification.public_trial',
                                   'IClassification.public_trial_statement'])

    @property
    def label(self):
        if IDossierMarker.providedBy(self.context):
            return _(u'Add Subdossier')
        else:
            portal_type = self.portal_type
            fti = getUtility(IDexterityFTI, name=portal_type)
            type_name = fti.Title()
            return pd_mf(u"Add ${name}", mapping={'name': type_name})


class DossierAddView(add.DefaultAddView):
    form = DossierAddForm
