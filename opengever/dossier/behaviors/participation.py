import base64

from five import grok
from persistent import Persistent
from persistent.list import PersistentList
from rwproperty import getproperty, setproperty
from z3c.formwidget.query.interfaces import IQuerySource
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import Interface, implements
import z3c.form

from Products.statusmessages.interfaces import IStatusMessage
from plone.directives import form
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.registry.interfaces import IRegistry
from plone.z3cform import layout

from opengever.dossier import _
from opengever.dossier.interfaces import IDossierParticipants

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
            # journal entry
            title = _(u'label_participant_added',
                      default=u'Participant added: ${contact} with roles ${roles}',
                      mapping={
                    'contact' : value.contact,
                    'roles' : value.role_list,
                    })
            # need to import here because of import loop
            from opengever.journal.handlers import journal_entry_factory
            journal_entry_factory(self.context, PARTICIPANT_ADDED,
                                  title, comment=value.comment)

    def has_participation(self, value):
        return value in self.get_participations()

    def remove_participation(self, value, quiet=True):
        if not quiet and not self.has_participation(value):
            raise ValueError('Participation not in list')
        lst = self.get_participations()
        lst.remove(value)
        self.set_participations(lst)
        # journal entry
        title = _(u'label_participant_removed',
                  default=u'Participant removed: ${contact}',
                  mapping={
                'contact' : value.contact,
                })
        # need to import here because of import loop
        from opengever.journal.handlers import journal_entry_factory
        journal_entry_factory(self.context, PARTICIPANT_REMOVED,
                              title)
        del value


# -------- model --------

class IParticipation(form.Schema):
    """ Participation Form schema
    """

    contact = schema.Choice(
        title = _(u'label_contact', default=u'Contact'),
        description = _(u'help_contact', default=u''),
        vocabulary = u'opengever.dossier.participation.contacts',
        required = True,
        )

    roles = schema.List(
        title = _(u'label_roles', default=u'Roles'),
        description = _(u'help_roles', default=u''),
        value_type = schema.Choice(
            vocabulary = u'opengever.dossier.participation.roles',
            ),
        required = False,
        )

    comment = schema.Text(
        title = _(u'label_comment', default=u'Comment'),
        description = _(u'help_comment', default=u''),
        required = False,
        )



# ------- vocabularies --------

class ContactVocabulary(SimpleVocabulary):
    grok.implements(IQuerySource)

    def search(self, query_string):
        return [v for v in self
                if query_string.lower() in v.value.lower()]


class ContactVocabularyFactory(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        for user in context.acl_users.getUsers():
            member_name = user.getProperty('fullname') or user.getName()
            email = user.getProperty('email', None)
            if email:
                member_name += ' ' + str(email)
            terms.append(SimpleVocabulary.createTerm(user.getId(),
                                                     str(user.getId()),
                                                     member_name))
        return ContactVocabulary(terms)

grok.global_utility(ContactVocabularyFactory,
                    name=u'opengever.dossier.participation.contacts')


class RolesVocabularyFactory(object):
    grok.implements(IVocabularyFactory)

    @property
    def roles(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IDossierParticipants)
        return getattr(proxy, 'roles', ())

    def __call__(self, context):
        terms = []
        for role in self.roles:
            role = str(role)
            terms.append(SimpleVocabulary.createTerm(role, role, role))
        return SimpleVocabulary(terms)

grok.global_utility(RolesVocabularyFactory,
                    name=u'opengever.dossier.participation.roles')


# --------- model class --------

class Participation(Persistent):
    """ A participation represents a relation between a contact and
    a dossier. The choosen contact can have one or more roles in this
    dossier.
    """
    implements(IParticipation)

    def __init__(self, contact, roles=[], comment=''):
        self.contact = contact
        self.roles = roles
        self.comment = comment
        notify(zope.lifecycleevent.ObjectCreatedEvent(self))

    @setproperty
    def roles(self, value):
        if value==None:
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
            return self.request.RESPONSE.redirect(
                self.context.absolute_url())

    @z3c.form.button.buttonAndHandler(_(u'button_cancel',
                                        default=u'Cancel'))
    def handle_cancel(self, action):
        url = self.context.absolute_url() + '/#participants-tab'
        return self.request.RESPONSE.redirect(url)



class ParticipationAddFormView(grok.CodeView, layout.FormWrapper):
    grok.context(IParticipationAwareMarker)
    grok.name('add-participation')
    form = ParticipationAddForm

    def __init__(self, *args, **kwargs):
        grok.CodeView.__init__(self, *args, **kwargs)
        layout.FormWrapper.__init__(self, *args, **kwargs)

    render = layout.FormWrapper.__call__


# ------- delete view -------
 
class DeleteParticipants(grok.CodeView):
    grok.context(IParticipationAwareMarker)
    grok.name('delete_participants')
    
    def render(self):
        phandler = IParticipationAware(self.context)
        for a in self.request.get('oids'):
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
            value = './#participants-tab'
        return value
