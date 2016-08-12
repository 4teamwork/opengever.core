from collective.elephantvocabulary import wrap_vocabulary
from five import grok
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.contact.models import Contact
from opengever.contact.models import Participation
from opengever.dossier import _
from plone import api
from plone.directives import form
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.z3cform import layout
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.interfaces import ActionExecutionError
from zope import schema
from zope.interface import Interface
from zope.interface import Invalid
import z3c.form


class IParticipation(form.Schema):
    """ Participation Form schema
    """

    contact = schema.Choice(
        title=_(u'label_contact', default=u'Contact'),
        description=_(u'help_contact', default=u''),
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
        default=[],
    )


class ParticipationAddForm(z3c.form.form.Form):
    ignoreContext = True
    label = _(u'label_add_participation', default=u'Add Participation')
    fields = z3c.form.field.Fields(IParticipation).omit('participation_id')

    fields['contact'].widgetFactory = AutocompleteFieldWidget
    fields['roles'].widgetFactory = CheckBoxFieldWidget

    @z3c.form.button.buttonAndHandler(_(u'button_add', default=u'Add'))
    def handle_add(self, action):
        data, errors = self.extractData()

        contact = Contact.query.get(data.get('contact'))
        oguid = Oguid.for_object(self.context)

        if Participation.query.by_oguid_and_contact(oguid, contact).count():
            raise ActionExecutionError(Invalid(
                _(u'msg_participation_already_exists',
                  u"There already exists a participation for this contact.")))

        if not errors:
            participation = Participation(contact=contact, dossier_oguid=oguid)
            create_session().add(participation)
            participation.add_roles(data.get('roles'))

            msg = _(u'info_participation_create', u'Participation created')
            api.portal.show_message(
                message=msg, request=self.request, type='info')
            return self.redirect_to_participants_tab()

    @z3c.form.button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.redirect_to_participants_tab()

    def redirect_to_participants_tab(self):
        return self.request.RESPONSE.redirect(
            '{}#participations'.format(self.context.absolute_url()))


class ParticipationAddFormView(layout.FormWrapper, grok.View):
    grok.context(Interface)
    grok.name('add-contact-participation')
    grok.require('cmf.AddPortalContent')
    form = ParticipationAddForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)
