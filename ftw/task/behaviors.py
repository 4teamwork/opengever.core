
from zope import schema
from zope.component import adapts
from zope.interface import Interface, implements, alsoProvides
from zope.annotation.interfaces import IAnnotations

from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.directives import form
from Products.CMFCore.utils import getToolByName

from rwproperty import getproperty, setproperty

from z3c.form.browser import radio

from ftw.task import _
from ftw.task import util


class ITransition(form.Schema):
    """ Behavior for enabling CMFEditions's versioning for dexterity
    content types. Be shure to enable versioning in the plone types
    control-panel for your content type.
    """
    form.widget(transition=radio.RadioFieldWidget)
    transition = schema.Choice(
        title=_("label_transition", default="Transition"),
        description=_(u"help_transition", default=""),
        source = util.getTransitionVocab,
        required = False,
    )

    form.fieldset(
        u'common',
        label = _(u'fieldset_common', default=u'Common'),
        fields = [
            u'transition',
            ],
        )

alsoProvides(ITransition, IFormFieldProvider)


class ITransitionMarker(Interface):
    """
    Marker Interface for the IVersionable behavior.
    """


class Transition(object):

    implements(ITransition)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    @getproperty
    def transition(self):
        return None

    @setproperty
    def transition(self, value):
        # store the value for later use (see events.py)
        annotation = IAnnotations(self.context.REQUEST)
        annotation['ftw.task.task'] = value
        if not self.context.title:
            ts = getToolByName(self.context, 'translation_service')
            self.context.id = ts.translate(value)
            self.context.title = ts.translate(value)
