from five import grok
from opengever.ogds.base.autocomplete_widget import AutocompleteMultiFieldWidget
from opengever.task import _
from opengever.task.task import ITask
from plone.directives import form
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from z3c.form import button
from zope import schema
from zope.interface import Interface


class IMultiTask(ITask):
    """A interface which could have multiple responsibles.
    """

    form.omitted('responsible_client')
    form.widget(responsible=AutocompleteMultiFieldWidget)
    responsible = schema.List(
        title=_(u'delegate_label_responsibles', default=u'Responsibles'),
        description=_(u'delegate_help_responsible',
                      default=u'Select one or more responsibles. For each selected '
                      u'responsible a subtask will be created and assigned.'),
        required=True,
        min_length=1,
        value_type=schema.Choice(
            vocabulary=u'opengever.ogds.base.AllUsersAndInboxesVocabulary')
    )


class MultiTaskForm(form.SchemaForm):
    grok.context(Interface)
    grok.name('multi_task')
    grok.require('zope2.View')

    ignoreContext = True
    label = _(u'heading_multi_task', u'Multi Task')
    schema = IMultiTask

    @button.buttonAndHandler(_(u'button_save', default=u'Save'))
    def save(self, action):
        pass

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def cancel(self, action):
        pass
