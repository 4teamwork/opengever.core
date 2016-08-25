from Acquisition import aq_parent
from collective.elephantvocabulary import wrap_vocabulary
from opengever.base.browser.modelforms import ModelAddForm
from opengever.base.browser.modelforms import ModelEditForm
from opengever.base.oguid import Oguid
from opengever.contact import _
from opengever.contact.models import Contact
from opengever.contact.models import Participation
from plone import api
from plone.directives import form
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.interfaces import ActionExecutionError
from z3c.form.interfaces import IDataConverter
from zope import schema
from zope.interface import Invalid
import z3c.form


class IParticipation(form.Schema):
    """ Participation Form schema
    """

    contact = schema.Choice(
        title=_(u'label_contact', default=u'Contact'),
        vocabulary=u'opengever.contact.ContactsVocabulary',
        required=True,
    )

    roles = schema.List(
        title=_(u'label_roles', default=u'Roles'),
        value_type=schema.Choice(
            source=wrap_vocabulary(
                'opengever.dossier.participation_roles',
                visible_terms_from_registry='opengever.dossier'
                '.interfaces.IDossierParticipants.roles'),
        ),
        required=True,
        missing_value=[],
    )


class ParticipationAddForm(ModelAddForm):
    label = _(u'label_add_participation', default=u'Add Participation')
    fields = z3c.form.field.Fields(IParticipation)
    model_class = Participation

    fields['contact'].widgetFactory = AutocompleteFieldWidget
    fields['roles'].widgetFactory = CheckBoxFieldWidget

    def validate(self, data):
        query = Participation.query.by_dossier(self.context).filter_by(
            contact_id=data.get('contact'))
        if query.count():
            raise ActionExecutionError(Invalid(
                _(u'msg_participation_already_exists',
                  u"There already exists a participation for this contact.")))

    def create(self, data):
        self.validate(data)
        participation = self.model_class(
            contact=Contact.query.get(data.get('contact')),
            dossier_oguid=Oguid.for_object(self.context))
        participation.add_roles(data.get('roles'))
        return participation

    def nextURL(self):
        return '{}#participations'.format(self.context.absolute_url())


class ParticipationEditForm(ModelEditForm):
    fields = z3c.form.field.Fields(IParticipation).omit('contact')
    fields['roles'].widgetFactory = CheckBoxFieldWidget

    def __init__(self, context, request):
        super(ParticipationEditForm, self).__init__(
            context, request, context.model)

    @property
    def label(self):
        return _(u'label_edit_participation',
                 default=u'Edit Participation of ${title}',
                 mapping={'title': self.model.contact.get_title()})

    def updateWidgets(self):
        super(ParticipationEditForm, self).updateWidgets()

        if self.request.method != 'GET':
            return

        widget = self.widgets['roles']
        widget.value = IDataConverter(widget).toWidgetValue(
            [role.role for role in self.model.roles])

        self.widgets.update()

    def applyChanges(self, data):
        self.model.update_roles(data.get('roles'))

    def nextURL(self):
        """Returns the url to the dossiers participation tab."""

        return '{}#participations'.format(
            aq_parent(self.context).absolute_url())


class ParticipationRemoveForm(z3c.form.form.Form):

    def __init__(self, context, request):
        super(ParticipationRemoveForm, self).__init__(context, request)
        self.model = context.model

    @property
    def label(self):
        return _(u'label_remove_participation',
                 default=u'Remove Participation of ${title}',
                 mapping={'title': self.model.contact.get_title()})

    @button.buttonAndHandler(_(u'Remove'), name='remove')
    def handleRemove(self, action):
        data, errors = self.extractData()
        if errors:
            return

        self.model.delete()

        api.portal.show_message(
            _(u'info_participation_removed', u'Participation removed'),
            api.portal.get().REQUEST)

        return self.request.RESPONSE.redirect(self.nextURL())

    @button.buttonAndHandler(
        _(u'label_cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.nextURL())

    def nextURL(self):
        """Returns the url to the dossiers participation tab."""

        return '{}#participations'.format(
            aq_parent(self.context).absolute_url())
