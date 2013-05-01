from Products.statusmessages.interfaces import IStatusMessage
from collective.elephantvocabulary import wrap_vocabulary
from five import grok
from opengever.dossier import _
from opengever.dossier import events
from persistent import Persistent
from persistent.list import PersistentList
from plone.directives import form
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.z3cform import layout
from rwproperty import getproperty, setproperty
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from zope.interface import Interface, implements
import base64
import z3c.form


_marker = object()
PARTICIPANT_ADDED = 'Participant added'
PARTICIPANT_REMOVED = 'Participant removed'


# ------ behavior ------

class IParticipationAware(Interface):
    """ Participation behavior interface. Types using this behaviors
    are able to have participations.
    """


class IParticipationAwareMarker(Interface):
    """ Marker interface for IParticipationAware behavior
    """


class ParticipationHandler(object):
    """ IParticipationAware behavior / adpter factory
    """
    implements(IParticipationAware)
    annotation_key = 'participations'

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)

    def create_participation(self, *args, **kwargs):
        p = Participation(*args, **kwargs)
        return p

    def get_participations(self):
        return self.annotations.get(self.annotation_key,
                                    PersistentList())

    def set_participations(self, value):
        if not isinstance(value, PersistentList):
            raise TypeError('Excpected PersistentList instance')
        self.annotations[self.annotation_key] = value

    def append_participiation(self, value):
        if not IParticipation.providedBy(value):
            raise TypeError('Excpected IParticipation object')
        if not self.has_participation(value):
            lst = self.get_participations()
            lst.append(value)
            self.set_participations(lst)
            notify(events.ParticipationCreated(self.context, value))

    def has_participation(self, value):
        return value in self.get_participations()

    def remove_participation(self, value, quiet=True):
        if not quiet and not self.has_participation(value):
            raise ValueError('Participation not in list')
        lst = self.get_participations()
        lst.remove(value)
        self.set_participations(lst)
        notify(events.ParticipationRemoved(self.context, value))
        del value


# -------- model --------

class IParticipation(form.Schema):
    """ Participation Form schema
    """

    contact = schema.Choice(
        title=_(u'label_contact', default=u'Contact'),
        description=_(u'help_contact', default=u''),
        vocabulary=u'opengever.ogds.base.ContactsAndUsersVocabulary',
        required=True,
        )

    roles = schema.List(
        title=_(u'label_roles', default=u'Roles'),
        description=_(u'help_roles', default=u''),
        value_type=schema.Choice(
            source=wrap_vocabulary(
                'opengever.dossier.participation_roles',
                visible_terms_from_registry='opengever.dossier'
                '.interfaces.IDossierParticipants.roles'),
            ),
        required=True,
        missing_value=[],
        )

# --------- model class --------


class Participation(Persistent):
    """ A participation represents a relation between a contact and
    a dossier. The choosen contact can have one or more roles in this
    dossier.
    """
    implements(IParticipation)

    def __init__(self, contact, roles=[]):
        self.contact = contact
        self.roles = roles

    @setproperty
    def roles(self, value):
        if value is None:
            pass
        elif not isinstance(value, PersistentList):
            value = PersistentList(value)
        self._roles = value

    @getproperty
    def roles(self):
        return self._roles

    @property
    def role_list(self):
        return ', '.join(self.roles)

    def has_key(self, key):
        return hasattr(self, key)


#  -------- add form -------

class ParticipationAddForm(z3c.form.form.Form):
    fields = z3c.form.field.Fields(IParticipation)
    label = _(u'label_participation', default=u'Participation')
    ignoreContext = True
    fields['contact'].widgetFactory = AutocompleteFieldWidget

    @z3c.form.button.buttonAndHandler(_(u'button_add', default=u'Add'))
    def handle_add(self, action):
        data, errors = self.extractData()
        if not errors:
            phandler = IParticipationAware(self.context)
            part = phandler.create_participation(**data)
            phandler.append_participiation(part)
            status = IStatusMessage(self.request)
            msg = _(u'info_participation_create',
                    u'Participation created')
            status.addStatusMessage(msg, type='info')
            return self._redirect_to_participants_tab()

    @z3c.form.button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self._redirect_to_participants_tab()

    def _redirect_to_participants_tab(self):
        url = self.context.absolute_url() + '/#participants'
        return self.request.RESPONSE.redirect(url)


class ParticipationAddFormView(layout.FormWrapper, grok.View):
    grok.context(IParticipationAwareMarker)
    grok.name('add-participation')
    grok.require('cmf.AddPortalContent')
    form = ParticipationAddForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)


# ------- delete view -------

class DeleteParticipants(grok.View):
    grok.context(IParticipationAwareMarker)
    grok.require('cmf.ModifyPortalContent')
    grok.name('delete_participants')

    def render(self):
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
                'Removed participations')
        status.addStatusMessage(msg, type='info')
        return self.request.RESPONSE.redirect(self.redirect_url)

    @property
    def redirect_url(self):
        value = self.request.get('orig_template')
        if not value:
            value = './#participants'
        return value
