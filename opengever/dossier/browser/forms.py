from Acquisition import aq_inner, aq_parent
from ftw.keywordwidget.widget import KeywordWidget
from opengever.base.behaviors.utils import hide_fields_from_behavior
from opengever.base.behaviors.utils import omit_classification_group
from opengever.base.vocabulary import wrap_vocabulary
from opengever.contact import _ as contact_mf
from opengever.dossier import _
from opengever.dossier import is_dossier_checklist_feature_enabled
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.participation import IParticipation
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.behaviors.protect_dossier import IProtectDossier
from opengever.dossier.behaviors.protect_dossier import IProtectDossierMarker
from opengever.dossier.widget import referenceNumberWidgetFactory
from opengever.kub import is_kub_feature_enabled
from opengever.ogds.base.sources import AllUsersAndGroupsSourceBinder
from plone import api
from plone.autoform.widgets import ParameterizedWidget
from plone.dexterity.browser import add
from plone.dexterity.browser import edit
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
from zope.security import checkPermission
import base64


def has_active_dossier_types(context):
    factory = wrap_vocabulary(
        'opengever.dossier.dossier_types',
        hidden_terms_from_registry='opengever.dossier.interfaces.IDossierType.hidden_dossier_types')

    # The elephantvocabulary does not consider the hidden terms when querying
    # for the  length, so we need to iterate.
    terms = [term for term in factory(context)]
    return len(terms) > 0


# TODO: temporary default value (autocompletewidget)
class DossierAddForm(add.DefaultAddForm):

    def render(self):
        fti = getUtility(IDexterityFTI, name=self.portal_type)
        if fti not in self.context.allowedContentTypes():
            raise Unauthorized

        return super(DossierAddForm, self).render()

    def update(self):
        # XXX: These methods will later be refactored to use a common helper
        # function to access group widgets in z3c forms.
        self.prefill_responsible()
        self.prefill_dossier_manager()
        super(DossierAddForm, self).update()

    def prefill_responsible(self):
        """Adds a default value for `responsible` to the request so the
        field is prefilled with the current user, or the parent dossier's
        responsible in the case of a subdossier.
        """
        if self.request.get('form.widgets.IDossier.responsible'):
            # Only prefill if no value set already
            return

        current_user = api.user.get_current().getId()
        self.request.set('form.widgets.IDossier.responsible', [current_user])

    def prefill_dossier_manager(self):
        """Prefill current user as dossier_manager in add forms.
        """
        if 'form.widgets.IProtectDossier.dossier_manager' in self.request.form:
            # Only prefill if no value set already - even if it's None / ''
            # Specifically, we don't want to override an empty value on the
            # save request (the one triggered when submitting the form)
            return

        current_user = api.user.get_current().getId()
        if not current_user:
            return

        try:
            AllUsersAndGroupsSourceBinder()(self.context).getTerm(current_user)
        except LookupError:
            # The current logged in user does not exist in the
            # field-source.
            return

        if 'Manager' in api.user.get_roles():
            # We don't want to prefill managers.
            return

        self.request.set('form.widgets.IProtectDossier.dossier_manager',
                         [current_user])

    def updateFields(self):
        super(DossierAddForm, self).updateFields()

        if checkPermission('opengever.base.EditLifecycleAndClassification', self.context):
            fields = ['IClassification.public_trial',
                      'IClassification.public_trial_statement']
        else:
            omit_classification_group(self)
            fields = []

        if not has_active_dossier_types(self.context):
            fields.append('IDossier.dossier_type')

        if not is_dossier_checklist_feature_enabled():
            fields.append('IDossier.checklist')

        hide_fields_from_behavior(self, fields)

    @property
    def label(self):
        if IDossierMarker.providedBy(self.context):
            return _(u'Add Subdossier')
        else:
            portal_type = self.portal_type
            fti = getUtility(IDexterityFTI, name=portal_type)
            type_name = fti.Title()
            return pd_mf(u"Add ${name}", mapping={'name': type_name})

    def add(self, object):
        super(DossierAddForm, self).add(object)

        # CUSTOM: Handle dossier protection after successfully adding
        # the dossier. To be able to set the localroles correctly, we need
        # the acquisition wrapped object.
        new_object = self.context.unrestrictedTraverse(object.getId())
        if IProtectDossierMarker.providedBy(new_object):
            IProtectDossier(new_object).protect()


class DossierAddView(add.DefaultAddView):
    form = DossierAddForm


class DossierEditForm(edit.DefaultEditForm):
    """Standard Editform, provide just a special label for subdossiers"""

    def updateFields(self):
        super(DossierEditForm, self).updateFields()

        # Add read-only field 'reference_number'
        # plone.autoform ingores read-only fields, but we want to display it in
        # the edit form.
        for group in self.groups:
            if group.label == u'fieldset_filing':
                group.fields += Fields(
                    IDossier['reference_number'], prefix='IDossier')
                group.fields['IDossier.reference_number'].widgetFactory = referenceNumberWidgetFactory
                group.fields['IDossier.reference_number'].mode = 'display'

        if checkPermission('opengever.base.EditLifecycleAndClassification', self.context):
            fields = ['IClassification.public_trial',
                      'IClassification.public_trial_statement']
        else:
            omit_classification_group(self)
            fields = []

        if not has_active_dossier_types(self.context):
            fields.append('IDossier.dossier_type')

        if not is_dossier_checklist_feature_enabled():
            fields.append('IDossier.checklist')

        hide_fields_from_behavior(self, fields)

    @property
    def label(self):
        if IDossierMarker.providedBy(aq_parent(aq_inner(self.context))):
            return _(u'Edit Subdossier')
        else:
            type_name = self.fti.Title()
            return pd_mf(u"Edit ${name}", mapping={'name': type_name})

    def applyChanges(self, data):
        changes = super(DossierEditForm, self).applyChanges(data)

        # CUSTOM: Handle dossier protection after editing the dossier.
        # Only update localroles if the user changed one of the IProtectDossier
        # fields
        if changes.get(IProtectDossier):
            IProtectDossier(self.context).protect()

        return changes


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
            status = IStatusMessage(self.request)
            if phandler.has_participation(data.get('contact')):
                msg = _(u'error_participant_already_exists',
                        default=u'There is already a participation for this contact.')
                status.addStatusMessage(msg, type='error')
            else:
                phandler.add_participation(data.get('contact'), data.get('roles'))
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


class DeleteParticipants(BrowserView):

    def __call__(self):
        oids = self.request.get('oids')
        if not oids:
            msg = _(u'warning_no_participants_selected',
                    default=u'You didn\'t select any participants.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.RESPONSE.redirect(self.redirect_url)
        if is_kub_feature_enabled():
            msg = contact_mf(
                u'warning_kub_contact_new_ui_only',
                default=u'Kub contacts are only supported in the new frontend')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.RESPONSE.redirect(self.redirect_url)
        phandler = IParticipationAware(self.context)
        for a in oids:
            oid = base64.decodestring(a)
            obj = self.context._p_jar[oid]
            phandler.remove_participation(obj.contact)
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
