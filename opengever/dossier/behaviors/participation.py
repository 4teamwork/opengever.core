from five import grok
from persistent import Persistent
from persistent.list import PersistentList
from rwproperty import getproperty, setproperty
from z3c.formwidget.query.interfaces import IQuerySource
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import Interface, implements
import z3c.form

from Products.statusmessages.interfaces import IStatusMessage
from plone.directives import form
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.z3cform import layout

from opengever.dossier import _

_marker = object()


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

    def create_participation(self, *args, **kwargs):
        return Participation(*args, **kwargs)

    def add_participation(self, participation):
        if not IParticipation.providedBy(participation):
            raise ValueError('Excpected participation to provide IParticipation')
        ann = IAnnotations(self.context)
        if getattr(ann, self.annotation_key, _marker)==_marker:
            ann[self.annotation_key] = PersistentList()
        ann[self.annotation_key].append(participation)

    def list_participation(self, participation):
        if getattr(ann, self.annotation_key, _marker)==_marker:
            ann[self.annotation_key] = PersistentList()
        return ann[self.annotation_key]


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
        return [
            'Mitwirkung',
            'Schlusszeichnung',
            'Kenntnisnahme',
            ]

    def __call__(self, context):
        terms = []
        for role in self.roles:
            role = str(role)
            terms.append(SimpleVocabulary.createTerm(role, role, role))
        return SimpleVocabulary(terms)

grok.global_utility(RolesVocabularyFactory,
                    name=u'opengever.dossier.participation.roles')


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


class ParticipationAddForm(z3c.form.form.Form):
    fields = z3c.form.field.Fields(IParticipation)
    label = _(u'label_participation', default=u'Participation')
    ignoreContext = True
    fields['contact'].widgetFactory = AutocompleteFieldWidget

    @z3c.form.button.buttonAndHandler(_(u'button_add', default=u'Add'))
    def handle_add(self, action):
        data, errors = self.extractData()
        if not errors:
            # XXX fix "Could not adapt" !?
            # phandler = IParticipationAware(self.context)
            phandler = ParticipationHandler(self.context)
            phandler.create_participation(**data)
            status = IStatusMessage(self.request)
            msg = _(u'info_participation_create',
                    u'Participation created')
            status.addStatusMessage(msg, type='info')
            return self.request.RESPONSE.redirect(
                self.context.absolute_url())
            


class ParticipationAddFormView(grok.CodeView, layout.FormWrapper):
    grok.context(IParticipationAwareMarker)
    grok.name('add-participation')
    form = ParticipationAddForm

    def __init__(self, *args, **kwargs):
        grok.CodeView.__init__(self, *args, **kwargs)
        layout.FormWrapper.__init__(self, *args, **kwargs)

    render = layout.FormWrapper.__call__
