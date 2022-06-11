from Acquisition import aq_parent
from ftw.keywordwidget.widget import KeywordWidget
from opengever.base.browser.modelforms import ModelAddForm
from opengever.base.browser.modelforms import ModelEditForm
from opengever.base.vocabulary import wrap_vocabulary
from opengever.contact import _
from opengever.contact.sources import ContactsSourceBinder
from plone import api
from plone.autoform.widgets import ParameterizedWidget
from plone.supermodel import model
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.interfaces import ActionExecutionError
from z3c.form.interfaces import IDataConverter
from zope import schema
from zope.interface import Invalid
import z3c.form


class IParticipation(model.Schema):
    """ Participation Form schema
    """

    contact = schema.Choice(
        title=_(u'label_contact', default=u'Contact'),
        source=ContactsSourceBinder(),
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

    fields['contact'].widgetFactory = ParameterizedWidget(
        KeywordWidget,
        async=True
    )
    fields['roles'].widgetFactory = CheckBoxFieldWidget

    @property
    def model_class(self):
        return self._participant.participation_class

    def validate(self, data):
        self._participant = data.get('contact')
        query = self.model_class.query.by_participant(
            self._participant).by_dossier(self.context)

        if query.count():
            raise ActionExecutionError(Invalid(
                _(u'msg_participation_already_exists',
                  u"There already exists a participation for this contact.")))

    def create(self, data):
        self.validate(data)
        return self.model_class.create(participant=self._participant,
                                       dossier=self.context,
                                       roles=data.pop('roles'))

    def add(self, obj):
        super(ParticipationAddForm, self).add(obj)
        self.context.reindexObject(idxs=["participations", "UID"])

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
                 default=u'Edit ${title}',
                 mapping={'title': self.model.get_title()})

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
        self.model.resolve_dossier().reindexObject(idxs=["participations", "UID"])

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
                 default=u'Remove ${title}',
                 mapping={'title': self.model.get_title()})

    @button.buttonAndHandler(_(u'Remove'), name='remove')
    def handleRemove(self, action):
        data, errors = self.extractData()
        if errors:
            return

        self.model.delete()
        self.model.resolve_dossier().reindexObject(idxs=["participations", "UID"])

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
