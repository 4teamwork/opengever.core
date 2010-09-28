import os
import datetime
from zope.i18n import translate
from z3c.form import form, field, button
from z3c.form.browser import radio
from zope.lifecycleevent import modified, ObjectModifiedEvent
from zope.interface import Interface
from zope.cachedescriptors.property import Lazy
from zope import schema
from zope.event import notify
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from five import grok

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from plone.memoize.view import memoize
from plone.z3cform import layout
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.autoform.form import AutoExtensibleForm

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from z3c.relationfield.schema import RelationChoice, RelationList
from z3c.relationfield.relation import RelationValue

from opengever.task import _
from opengever.task.adapters import IResponseContainer, Response
from opengever.task.interfaces import IResponseAdder
from opengever.task.permissions import DEFAULT_ISSUE_MIME_TYPE
from opengever.task import util
from opengever.task.task import ITask
from opengever.task.source import DossierPathSourceBinder
from ftw.datepicker.widget import DatePickerFieldWidget


class IResponse(Interface):
    text = schema.Text(
        title = _('label_response', default="Response"),
        description=_('help_response', default=""),
        required = False,
        )

    responsible_client = schema.Choice(
        title=_(u'label_resonsible_client',
                default=u'Responsible Client'),
        description=_(u'help_responsible_client',
                      default=u''),
        vocabulary='opengever.ogds.base.ClientsVocabulary',
        required=True)

    responsible = schema.Choice(
        title=_(u"label_responsible_Response", default="New responsible"),
        description =_(u"help_new_responsible_response", default=""),
        vocabulary=u'opengever.ogds.base.UsersAndInboxesVocabulary',
        required = False,
        )

    deadline = schema.Date(
        title=_(u"label_deadline_Response", default=u"New deadline"),
        description=_(u"help_deadline_response", default=""),
        required = False,
        )

    date_of_completion = schema.Date(
        title=_(u"label_date_of_completion", default=u"Date of completion"),
        description=_(u"help_date_of_completion", default=u""),
        required = False,
        )

    transition = schema.Choice(
        title=_("label_transition", default="Transition"),
        description=_(u"help_transition", default=""),
        source = util.getTransitionVocab,
        required = False,
        )

    relatedItems = RelationList(
        title=_(u'label_related_items', default=u'Related Items'),
        default=[],
        value_type=RelationChoice(title=u"Related",
                                  source=DossierPathSourceBinder(
                navigation_tree_query=
                {'portal_type': 'opengever.document.document', },
                portal_type="opengever.document.document", ),
                                  ),
        required=False,
        )


def voc2dict(vocab, current=None):
    """Make a dictionary from a vocabulary.

    >>> from Products.Archetypes.atapi import DisplayList
    >>> vocab = DisplayList()
    >>> vocab.add('a', "The letter A")
    >>> voc2dict(vocab)
    [{'checked': '', 'value': 'a', 'label': 'The letter A'}]
    >>> vocab.add('b', "The letter B")
    >>> voc2dict(vocab)
    [{'checked': '', 'value': 'a', 'label': 'The letter A'},
    {'checked': '', 'value': 'b', 'label': 'The letter B'}]
    >>> voc2dict(vocab, current='c')
    [{'checked': '', 'value': 'a', 'label': 'The letter A'},
    {'checked': '', 'value': 'b', 'label': 'The letter B'}]
    >>> voc2dicts(vocab, current='b')
    [{'checked': '', 'value': 'a', 'label': 'The letter A'},
    {'checked': 'checked', 'value': 'b', 'label': 'The letter B'}]

    """
    options = []
    for value, label in vocab.items():
        checked = (value == current) and "checked" or ""
        options.append(dict(value=value, label=label,
                            checked=checked))
    return options


class Base(BrowserView):
    """Base view for PoiIssues.

    Mostly meant as helper for adding a response.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.folder = IResponseContainer(context)
        self.mimetype = DEFAULT_ISSUE_MIME_TYPE
        self.use_wysiwyg = (self.mimetype == 'text/html')

    def responses(self):
        context = aq_inner(self.context)
        trans = context.portal_transforms
        items = []
        #linkDetection = context.linkDetection
        for id, response in enumerate(self.folder):
            # Use the already rendered response when available
            if response.rendered_text is None:
                if response.mimetype == 'text/html':
                    html = response.text
                elif response.text == None:
                    html = ""
                else:
                    html = trans.convertTo('text/html',
                                           response.text,
                                           mimetype=response.mimetype)
                    html = html.getData()
                # Detect links like #1 and r1234
                #html = linkDetection(html)
                response.rendered_text = html
            html = response.rendered_text
            info = dict(id=id,
                        response=response,
                        #relatedItems=getattr(response,"relatedItems",()),
                        html=html)
            items.append(info)
            # reverse the items, so that the latest one is above
            items.reverse()
        return items

    @property
    @memoize
    def portal_url(self):
        context = aq_inner(self.context)
        plone = context.restrictedTraverse('@@plone_portal_state')
        return plone.portal_url()

    @Lazy
    def memship(self):
        context = aq_inner(self.context)
        return getToolByName(context, 'portal_membership')

    @property
    @memoize
    def can_edit_response(self):
        context = aq_inner(self.context)
        return self.memship.checkPermission('Poi: Edit response', context)

    @property
    @memoize
    def can_delete_response(self):
        context = aq_inner(self.context)
        return self.memship.checkPermission('Delete objects', context)

    def validate_response_id(self):
        """Validate the response id from the request.

        Return -1 if for example the response id does not exist.
        Return the response id otherwise.

        Side effect: an informative status message is set.
        """
        status = IStatusMessage(self.request)
        response_id = self.request.form.get('response_id', None)
        if response_id is None:
            msg = _(u"No response selected.")
            msg = translate(msg, 'Poi', context=self.request)
            status.addStatusMessage(msg, type='error')
            return -1
        else:
            try:
                response_id = int(response_id)
            except ValueError:
                msg = _(u"Response id ${response_id} is no integer.",
                        mapping=dict(response_id=response_id))
                msg = translate(msg, 'Poi', context=self.request)
                status.addStatusMessage(msg, type='error')
                return -1
            if response_id >= len(self.folder):
                msg = _(u"Response id ${response_id} does not exist.",
                        mapping=dict(response_id=response_id))
                msg = translate(msg, 'Poi', context=self.request)
                status.addStatusMessage(msg, type='error')
                return -1
            else:
                return response_id
        # fallback
        return -1

    @property
    def severity(self):
        context = aq_inner(self.context)
        return context.getSeverity()

    @property
    def targetRelease(self):
        context = aq_inner(self.context)
        return context.getTargetRelease()

    @property
    def responsibleManager(self):
        context = aq_inner(self.context)
        return context.getResponsibleManager()


class AddForm(form.AddForm, AutoExtensibleForm):
    fields = field.Fields(IResponse)
    fields['responsible'].widgetFactory = AutocompleteFieldWidget
    fields['transition'].widgetFactory = radio.RadioFieldWidget
    fields['deadline'].widgetFactory = DatePickerFieldWidget
    fields = fields.omit('date_of_completion')

    @property
    def action(self):
        """See interfaces.IInputForm"""
        return os.path.join(self.request.getURL(),
                            '++add++opengever.task.task')

    @button.buttonAndHandler(_(u'add', default='Add'),
                             name='add', )

    def handleContinue(self, action):
        data, errors = self.extractData()
        if errors:
            errorMessage ='<ul>'
            for error in errors:
                if errorMessage.find(error.message):
                    errorMessage += '<li>' + error.message + '</li>'
            errorMessage += '</ul>'
            self.status = errorMessage
        else:
            new_response = Response(data.get('text'))
            #define responseTyp
            responseCreator = new_response.creator
            task = aq_inner(self.context)

            if responseCreator == '(anonymous)':
                new_response.type = 'additional'
            if responseCreator == task.Creator():
                new_response.type = 'clarification'
            #if util.getManagersVocab.getTerm(responseCreator):
            #   new_response.type =  'reply'
            #check transition
            if data.get('transition', None) == 'task-transition-open-resolved':
                completion_date = datetime.datetime.now().date()
            else:
                completion_date = None

            #check other fields
            options = [
                (task.deadline, data.get('deadline'), 'deadline',
                 _('deadline')),
                (task.date_of_completion, completion_date,
                 'date_of_completion', _('date_of_completion'))]

            for task_field, resp_field, option, title in options:
                if resp_field and task_field != resp_field:
                    new_response.add_change(option,
                                            title,
                                            task_field,
                                            resp_field)
                    task.__setattr__(option, resp_field)

            # change the responsible
            responsible = data.get('responsible')
            responsible_client = data.get('responsible_client')
            if responsible and responsible != task.responsible:
                new_response.add_change('responsible',
                                        _('responsible'),
                                        task.responsible,
                                        responsible)
                task.responsible = responsible
                task.responsible_client = responsible_client

            # save relatedItems on task
            relatedItems = data.get('relatedItems')
            intids = getUtility(IIntIds)
            for item in relatedItems:
                to_id = intids.getId(item)
                if task.get('relatedItems'):
                    task.relatedItems.append(RelationValue(to_id))
                else:
                    setattr(task, 'relatedItems', [RelationValue(to_id)])
                new_response.add_change('relatedItems',
                                        _('label_related_items', default="Related Items"),
                                        '',
                                        item.Title())

            # change workflow state of task
            if data.get('transition'):
                wftool = getToolByName(self.context, 'portal_workflow')
                before = wftool.getInfoFor(self.context, 'review_state')
                if data.get('transition') != before:
                    before = wftool.getTitleForStateOnType(before, task.Type())
                    wftool.doActionFor(self.context, data.get('transition'))
                    after = wftool.getInfoFor(self.context, 'review_state')
                    after = wftool.getTitleForStateOnType(after, task.Type())
                    new_response.add_change('review_state', _(u'Issue state'),
                                            before, after)

            container = IResponseContainer(self.context)
            container.add(new_response)

            notify(ObjectModifiedEvent(self.context))

            copy_related_documents_view = self.context.restrictedTraverse(
                '@@copy-related-documents-to-inbox')
            if copy_related_documents_view.available():
                url = os.path.join(self.context.absolute_url(),
                                   '@@copy-related-documents-to-inbox')
            else:
                url = self.context.absolute_url()
            self.request.RESPONSE.redirect(url)

    @button.buttonAndHandler(_(u'cancel', default='Cancel'),
                             name='cancel', )

    def handleCancel(self, action):
        return self.request.RESPONSE.redirect('.')


class BeneathTask(grok.ViewletManager):
    grok.context(ITask)
    grok.name('opengever.task.beneathTask')


class ResponseView(grok.Viewlet, Base):
    grok.context(ITask)
    grok.name("opengever.task.response.view")
    grok.viewletmanager(BeneathTask)
    grok.order(1)

    def __init__(self, context, request, view, manager):
        grok.Viewlet.__init__(self, context, request, view, manager)
        Base.__init__(self, context, request)

"""
class AddFormView(layout.FormWrapper, grok.Viewlet, Base):
grok.implements(IResponseAdder)
grok.context(ITask)
grok.name("opengever.task.response.addForm")
grok.viewletmanager(BeneathTask)
grok.order(2)
form = AddForm
def __init__(self, context, request, view, manager):
layout.FormWrapper.__init__(self,context,request)
grok.Viewlet.__init__(self,context,request,view, manager)
Base.__init__(self,context, request)
self.__parent__ = view
self.form_instance.view = self

def render(self):
return layout.FormWrapper.render_form(self)
"""


class SingleAddFormView(layout.FormWrapper, grok.CodeView):
    grok.implements(IResponseAdder)
    grok.context(ITask)
    grok.name("addresponse")

    form = AddForm

    def __init__(self, context, request):
        layout.FormWrapper.__init__(self, context, request)
        grok.CodeView.__init__(self, context, request)


class Edit(Base):

    @property
    @memoize
    def response(self):
        form = self.request.form
        response_id = form.get('response_id', None)
        if response_id is None:
            return None
        try:
            response_id = int(response_id)
        except ValueError:
            return None
        if response_id >= len(self.folder):
            return None
        return self.folder[response_id]

    @property
    def response_found(self):
        return self.response is not None


class Save(Base):

    def __call__(self):
        form = self.request.form
        context = aq_inner(self.context)
        status = IStatusMessage(self.request)
        if not self.can_edit_response:
            msg = _(u"You are not allowed to edit responses.")
            msg = translate(msg, 'Poi', context=self.request)
            status.addStatusMessage(msg, type='error')
        else:
            response_id = form.get('response_id', None)
            if response_id is None:
                msg = _(u"No response selected for saving.")
                msg = translate(msg, 'Poi', context=self.request)
                status.addStatusMessage(msg, type='error')
            else:
                response = self.folder[response_id]
                response_text = form.get('response', u'')
                response.text = response_text
                # Remove cached rendered response.
                response.rendered_text = None
                msg = _(u"Changes saved to response id ${response_id}.",
                        mapping=dict(response_id=response_id))
                msg = translate(msg, 'Poi', context=self.request)
                status.addStatusMessage(msg, type='info')
                # Fire event.  We put the context in the descriptions
                # so event handlers can use this fully acquisition
                # wrapped object to do their thing.  Feels like
                # cheating, but it gets the job done.  Arguably we
                # could turn the two arguments around and signal that
                # the issue has changed, with the response in the
                # event descriptions.
                modified(response, context)
        self.request.response.redirect(context.absolute_url())


class Delete(Base):

    def __call__(self):
        context = aq_inner(self.context)
        status = IStatusMessage(self.request)

        if not self.can_delete_response:
            msg = _(u"You are not allowed to delete responses.")
            msg = translate(msg, 'Poi', context=self.request)
            status.addStatusMessage(msg, type='error')
        else:
            response_id = self.request.form.get('response_id', None)
            if response_id is None:
                msg = _(u"No response selected for removal.")
                msg = translate(msg, 'Poi', context=self.request)
                status.addStatusMessage(msg, type='error')
            else:
                try:
                    response_id = int(response_id)
                except ValueError:
                    msg = _(u"Response id ${response_id} is no integer so it "
                            "cannot be removed.",
                            mapping=dict(response_id=response_id))
                    msg = translate(msg, 'Poi', context=context)
                    status.addStatusMessage(msg, type='error')
                    self.request.response.redirect(context.absolute_url())
                    return
                if response_id >= len(self.folder):
                    msg = _(u"Response id ${response_id} does not exist so it "
                            "cannot be removed.",
                            mapping=dict(response_id=response_id))
                    msg = translate(msg, 'Poi', context=context)
                    status.addStatusMessage(msg, type='error')
                else:
                    self.folder.delete(response_id)
                    msg = _(u"Removed response id ${response_id}.",
                            mapping=dict(response_id=response_id))
                    status.addStatusMessage(msg, type='info')
        self.request.response.redirect(context.absolute_url())
