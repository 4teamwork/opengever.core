from Acquisition import aq_inner
from five import grok
from opengever.activity.events import TaskNotifactionEvent
from opengever.base.source import DossierPathSourceBinder
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.base.utils import ogds_service
from opengever.tabbedview.helper import linked
from opengever.task import _
from opengever.task import util
from opengever.task.adapters import IResponseContainer
from opengever.task.adapters import Response
from opengever.task.interfaces import IResponseAdder
from opengever.task.interfaces import IWorkflowStateSyncer
from opengever.task.permissions import DEFAULT_ISSUE_MIME_TYPE
from opengever.task.task import ITask
from plone.autoform.form import AutoExtensibleForm
from plone.memoize.view import memoize
from plone.z3cform import layout
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.browser import radio
from z3c.form.interfaces import HIDDEN_MODE
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.cachedescriptors.property import Lazy
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.event import notify
from zope.i18n import translate
from zope.interface import Interface
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import modified
from zope.lifecycleevent import ObjectModifiedEvent
import datetime
import os


class IResponse(Interface):

    transition = schema.Choice(
        title=_("label_transition", default="Transition"),
        description=_(u"help_transition", default=""),
        source=util.getTransitionVocab,
        required=False,
        )

    text = schema.Text(
        title=_('label_response', default="Response"),
        description=_('help_response', default=""),
        required=False,
        )

    date_of_completion = schema.Date(
        title=_(u"label_date_of_completion", default=u"Date of completion"),
        description=_(u"help_date_of_completion", default=u""),
        required=False,
        )

    relatedItems = RelationList(
        title=_(u'label_related_items', default=u'Related Items'),
        default=[],
        value_type=RelationChoice(
            title=u"Related",
            source=DossierPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                ),
            ),
        required=False,
        )


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
                elif response.text is None:
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
                        html=html)
            items.append(info)

        # sort the items, so that the latest one is at top
        items.sort(lambda a, b: cmp(b['response'].date,
                                    a['response'].date))
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


class AddForm(form.AddForm, AutoExtensibleForm):
    fields = field.Fields(IResponse)
    fields['transition'].widgetFactory = radio.RadioFieldWidget
    fields = fields.omit('date_of_completion')

    @property
    def label(self):
        transition = self.request.get('form.widgets.transition',
                                      self.request.get('transition', None))

        label = [self.context.Title().decode('utf-8')]
        if transition:
            label.append(translate(transition, domain='plone',
                                   context=self.request))
        return u': '.join(label)

    def updateActions(self):
        super(AddForm, self).updateActions()
        self.actions["save"].addClass("context")

    @button.buttonAndHandler(_(u'save', default='Save'),
                             name='save')
    def handleSubmit(self, action):
        data, errors = self.extractData()
        if errors:
            errorMessage = '<ul>'
            for error in errors:
                if errorMessage.find(error.message):
                    errorMessage += '<li>' + error.message + '</li>'
            errorMessage += '</ul>'
            self.status = errorMessage
            return None

        else:
            new_response = Response(data.get('text'))
            #define responseTyp
            responseCreator = new_response.creator
            task = aq_inner(self.context)

            if responseCreator == '(anonymous)':
                new_response.type = 'additional'
            if responseCreator == task.Creator():
                new_response.type = 'clarification'

            if data.get('transition', None):
                new_response.transition = data.get('transition', None)

            #if util.getManagersVocab.getTerm(responseCreator):
            #   new_response.type =  'reply'
            #check transition
            if data.get('transition', None) in (
                'task-transition-open-resolved',
                'task-transition-in-progress-resolved'):

                completion_date = datetime.date.today()

            else:
                completion_date = None

            #check other fields
            options = [
                # (task.deadline, data.get('deadline'), 'deadline',
                #  _('deadline')),
                (task.date_of_completion, completion_date,
                 'date_of_completion', _('date_of_completion'))]
            for task_field, resp_field, option, title in options:
                if resp_field and task_field != resp_field:
                    new_response.add_change(option,
                                            title,
                                            task_field,
                                            resp_field)
                    task.__setattr__(option, resp_field)

            # save relatedItems on task
            related_ids = []
            if getattr(task, 'relatedItems'):
                related_ids = [item.to_id for item in task.relatedItems]

            relatedItems = data.get('relatedItems') or []
            intids = getUtility(IIntIds)
            for item in relatedItems:
                to_id = intids.getId(item)
                # relation allready exists
                item._v__is_relation = True
                if to_id not in related_ids:
                    if getattr(task, 'relatedItems'):
                        task.relatedItems.append(RelationValue(to_id))
                    else:
                        setattr(task, 'relatedItems', [RelationValue(to_id)])

                new_response.add_change('relatedItems',
                                        _(u'label_related_items',
                                          default=u"Related Items"),
                                        '',
                                        linked(item, item.Title()))

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
            notify(TaskNotifactionEvent(self.context, new_response))

            if data.get('transition'):
                syncer = getMultiAdapter((self.context, self.request),
                                         IWorkflowStateSyncer)
                syncer.change_remote_tasks_workflow_state(
                    data.get('transition'), text=data.get('text'))

            copy_related_documents_view = self.context.restrictedTraverse(
                '@@copy-related-documents-to-inbox')
            if copy_related_documents_view.available():
                url = os.path.join(self.context.absolute_url(),
                                   '@@copy-related-documents-to-inbox')
            else:
                url = self.context.absolute_url()
            self.request.RESPONSE.redirect(url)
            return new_response

    @button.buttonAndHandler(_(u'cancel', default='Cancel'),
                             name='cancel', )
    def handleCancel(self, action):
        return self.request.RESPONSE.redirect('.')

    def updateWidgets(self):
        form.AddForm.updateWidgets(self)
        if self.context.portal_type == 'opengever.inbox.forwarding':
            self.widgets['relatedItems'].mode = HIDDEN_MODE
        if not self.is_user_assigned_to_current_org_unit():
            self.widgets['relatedItems'].mode = HIDDEN_MODE

        self.widgets['transition'].mode = HIDDEN_MODE

    def is_user_assigned_to_current_org_unit(self):
        units = ogds_service().assigned_org_units()
        return get_current_org_unit() in units


class SingleAddFormView(layout.FormWrapper, grok.View):
    grok.implements(IResponseAdder)
    grok.context(ITask)
    grok.name("addresponse")
    grok.require('cmf.AddPortalContent')

    form = AddForm

    def __init__(self, context, request):
        layout.FormWrapper.__init__(self, context, request)
        grok.View.__init__(self, context, request)


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
