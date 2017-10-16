from AccessControl import getSecurityManager
from ftw.keywordwidget.widget import KeywordWidget
from opengever.base.behaviors.utils import hide_fields_from_behavior
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.participation import IParticipation
from opengever.dossier.behaviors.participation import IParticipationAware
from plone.autoform.widgets import ParameterizedWidget
from plone.dexterity.browser import add
from plone.dexterity.i18n import MessageFactory as pd_mf  # noqa
from plone.dexterity.interfaces import IDexterityFTI
from plone.z3cform import layout
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.field import Fields
from z3c.form.form import Form
from zExceptions import Unauthorized
from zope.component import getUtility
import base64


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

#  -------- add form -------


class ParticipationAddForm(Form):
    fields = Fields(IParticipation)
    label = _(u'label_participation', default=u'Participation')
    ignoreContext = True
    fields['contact'].widgetFactory = ParameterizedWidget(
        KeywordWidget,
        async=True
    )

    fields['roles'].widgetFactory = CheckBoxFieldWidget

    @button.buttonAndHandler(_(u'button_add', default=u'Add'))
    def handle_add(self, action):
        data, errors = self.extractData()
        if not errors:
            phandler = IParticipationAware(self.context)
            part = phandler.create_participation(**data)
            phandler.append_participiation(part)
            status = IStatusMessage(self.request)
            msg = _(u'info_participation_create',
                    u'Participation created.')
            status.addStatusMessage(msg, type='info')
            return self._redirect_to_participants_tab()

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self._redirect_to_participants_tab()

    def _redirect_to_participants_tab(self):
        url = self.context.absolute_url() + '/#participants'
        return self.request.RESPONSE.redirect(url)


class ParticipationAddFormView(layout.FormWrapper):

    form = ParticipationAddForm


# ------- delete view -------

class DeleteParticipants(BrowserView):

    def __call__(self):
        oids = self.request.get('oids')
        if not oids:
            msg = _(u'warning_no_participants_selected',
                    default=u'You didn\'t select any participants.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.RESPONSE.redirect(self.redirect_url)
        phandler = IParticipationAware(self.context)
        for a in oids:
            oid = base64.decodestring(a)
            obj = self.context._p_jar[oid]
            phandler.remove_participation(obj)
        status = IStatusMessage(self.request)
        msg = _(u'info_removed_participations',
                'Removed participations.')
        status.addStatusMessage(msg, type='info')
        return self.request.RESPONSE.redirect(self.redirect_url)

    @property
    def redirect_url(self):
        value = self.request.get('orig_template')
        if not value:
            value = './#participants'
        return value
