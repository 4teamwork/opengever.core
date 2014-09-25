from Acquisition import aq_inner, aq_parent
from datetime import datetime
from five import grok
from opengever.inbox import _
from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from opengever.ogds.base.utils import get_current_org_unit
from opengever.task import _ as task_mf
from opengever.task.task import ITask, Task
from plone.directives import form
from plone.directives.dexterity import AddForm
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.app.container.interfaces import IObjectAddedEvent
from zope.i18n import translate
from zope.interface import implements


class IForwarding(ITask):
    """Schema interface for forwardings.
    """

    # common fieldset
    form.omitted('task_type')

    # only hide relatedItems - we need it for remembering which documents
    # should be moved after creation when creating forwarding from tabbed view.
    form.mode(relatedItems=HIDDEN_MODE)

    # additional fieldset
    form.omitted('expectedStartOfWork')
    form.omitted('expectedDuration')
    form.omitted('expectedCost')
    form.omitted('effectiveDuration')
    form.omitted('effectiveCost')

    #only hide date_of_completion, it's used
    form.mode(date_of_completion=HIDDEN_MODE)

    # deadline is not required
    deadline = schema.Date(
        title=task_mf(u"label_deadline", default=u"Deadline"),
        description=task_mf(u"help_deadline", default=u""),
        required=False,
        )

    form.widget(responsible=AutocompleteFieldWidget)
    responsible = schema.Choice(
        title=_(u"label_responsible", default=u"Responsible"),
        description=_(u"help_responsible", default=""),
        vocabulary=u'opengever.ogds.base.InboxesVocabulary',
        required=True,
        )


class Forwarding(Task):
    """Forwarding model class.
    """
    implements(IForwarding)

    @property
    def task_type_category(self):
        """Generates a Property for task categories"""
        return None

    def get_static_task_type(self):

        """Provide a marker string, which will be translated
           in the tabbedview helper method.
        """
        return 'forwarding_task_type'

    def set_static_task_type(self, value):
        """Marker set function"""
        # do not fail when trying to set the task type - but ignore
        return

    task_type = property(get_static_task_type, set_static_task_type)

    def get_task_type_label(self, language=None):
        label = _('forwarding_task_type', default=u'Forwarding')
        if language:
            return translate(label, context=self.REQUEST,
                             domain='opengever.inbox',
                             target_language=language)
        return label


class ForwardingAddForm(AddForm):
    """Provide a custom add-form which adds the selected documents
    (tabbed_view) to the hidden relatedItems field and sets some defaults.
    The documents are later moved by move_documents_into_forwarding (see
    below).
    """
    grok.name('opengever.inbox.forwarding')

    def update(self):
        """put default value for relatedItems into request - the added
           objects will later be moved insed the forwarding
        """
        paths = self.request.get('paths', [])

        if not (paths or
                self.request.form.get('form.widgets.relatedItems', [])
        or '@@autocomplete-search' in self.request.get('ACTUAL_URL', '')):
            # add status message and redirect current window back to inbox
            # but ONLY if we're not in a z3cform_inline_validation or
            # autocomplete-search request!
            IStatusMessage(self.request).addStatusMessage(
                _(u'error_no_document_selected',
                  u'Error: Please select at least one document to forward'),
                type='error')
            redir_url = self.request.get('orig_template',
                                         self.context.absolute_url())
            self.request.RESPONSE.redirect(redir_url)

        if paths:
            self.request.set('form.widgets.relatedItems', paths)

        # put default value for issuer into request
        if not self.request.get('form.widgets.issuer', None):
            self.request.set('form.widgets.issuer',
                             get_current_org_unit().inbox().id())

        # put the default responsible into the request
        if not self.request.get('form.widgets.responsible_client', None):
            org_unit = get_current_org_unit()
            self.request.set('form.widgets.responsible_client', org_unit.id())
            self.request.set('form.widgets.responsible',
                             [org_unit.inbox().id()])

        super(ForwardingAddForm, self).update()


@grok.subscribe(IForwarding, IObjectAddedEvent)
def move_documents_into_forwarding(context, event):
    """When selecting documents in the tabbed view and creating a
    forwarding with this documents, they'll be added to the hidden field
    "relatedItems" (see custom AddForm above) - which is not yet the right
    place. After saving the forwarding, we need to move the documents into
    the forwarding (which did not exist before).
    """
    relations = context.relatedItems
    for relation in relations:
        obj = relation.to_object
        clipboard = aq_parent(aq_inner(obj)).manage_cutObjects(obj.id)
        context.manage_pasteObjects(clipboard)
    context.relatedItems = []


@grok.subscribe(IForwarding, IActionSucceededEvent)
def set_dates(context, event):
    """Eventhandler wich set automaticly the enddate
    when a forwarding would be closed"""

    closing_transitions = [
        'forwarding-transition-close',
        'forwarding-transition-assign-to-dossier']

    if event.action in closing_transitions:
        context.date_of_completion = datetime.now()
