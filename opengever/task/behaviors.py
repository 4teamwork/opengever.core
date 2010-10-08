from Products.CMFCore.utils import getToolByName
from opengever.base.interfaces import ISequenceNumber
from opengever.task import _
from opengever.task import util
from plone.app.content.interfaces import INameFromTitle
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.directives import form
from rwproperty import getproperty, setproperty
from z3c.form.browser import radio
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.component import getUtility
from zope.interface import Interface, implements, alsoProvides


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
        required = True,
    )

    # form.fieldset(
    #     u'common',
    #     label = _(u'fieldset_common', default=u'Common'),
    #     fields = [
    #         u'transition',
    #         ],
    #     )

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
        annotation['opengever.task.task'] = value
        if not self.context.title:
            ts = getToolByName(self.context, 'translation_service')
            self.context.id = ts.translate(value)
            self.context.title = ts.translate(value)


class ITaskNameFromTitle(INameFromTitle):
    """Behavior interface.
    """


class TaskNameFromTitle(object):
    """Speical name from title behavior for letting the normalizing name
    chooser choose the ID like want it to be.
    The of a task should be in the format: "task-{sequence number}"
    """

    implements(ITaskNameFromTitle)

    format = u'task-%i'

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        seq_number = getUtility(ISequenceNumber).get_number(self.context)
        return self.format % seq_number

