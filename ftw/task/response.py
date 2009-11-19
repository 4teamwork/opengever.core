from zope.i18n import translate
from z3c.form import form, field, button
from zope.lifecycleevent import modified
from zope.interface import implements, Interface
from zope.cachedescriptors.property import Lazy
from zope import schema
from five import grok


from OFS.Image import File
from AccessControl import Unauthorized
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from plone.memoize.view import memoize
from plone.z3cform import layout
from plone.formwidget.autocomplete import AutocompleteFieldWidget


from Products.Archetypes.atapi import DisplayList
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.utils import contentDispositionHeader

from ftw.task import _
from ftw.task import permissions
from ftw.task.adapters import IResponseContainer, Response
from ftw.task.interfaces import IResponseAdder
from ftw.task.permissions import DEFAULT_ISSUE_MIME_TYPE
from ftw.task import util
from ftw.task.task import ITask

try:
    from plone.i18n.normalizer.interfaces import \
        IUserPreferredFileNameNormalizer
    FILE_NORMALIZER = True
except ImportError:
    FILE_NORMALIZER = False


def pretty_size(size):
    if size <= 0:
        return "0 Kb"
    kb = size / 1024
    size = "%d Kb" % kb
    if kb > 999:
        mb = kb / 1024
        size = "%d Mb" % mb
        if mb > 999:
            gb = mb / 1024
            size = "%d Gb" % gb
    return size

class IResponse(Interface):
    text =  schema.Text(
        title = _('label_response', default="Response"),
        description=_('help_response', default=""),
        required = True,
    )

    #form.widget(responsible=AutocompleteFieldWidget)
    new_responsible = schema.Choice(
        title=_(u"label_responsible_Response", default="Responsible"),
        description =_(u"help_responsible_response", default=""),
        source = util.getManagersVocab,
        required = False,
    )

    deadline = schema.Datetime(
        title=_(u"label_deadline_Response", default=u"Deadline"),
        description=_(u"help_deadline_response"),
        required = False, 
    )

    transition = schema.Choice(
        title=_("label_transition", default="Transition"),
        description=_(u"help_transition", default=""),
        source = util.getTransitionVocab,
        required = False,
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
    >>> voc2dict(vocab, current='b')
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

    @property
    @memoize
    def upload_allowed(self):
        """Is the user allowed to upload on attachment?
        """
        context = aq_inner(self.context)
        return self.memship.checkPermission(
            permissions.UploadAttachment, context)


class AddForm(form.AddForm):
    fields = field.Fields(IResponse)
    #XXX use AutocompleteFieldWidget
    #fields['new_responsible'].widgetFactory = AutocompleteFieldWidget
    
    @property
    def action(self):
        """See interfaces.IInputForm"""
        return os.path.join(self.request.getURL(), '++add++ftw.task.task')
    
    @button.buttonAndHandler(_(u'add', default='Add'),
                             name='add',)

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
            #define responseTy              
            responseCreator = new_response.creator
            task = aq_inner(self.context)
            
            if responseCreator == '(anonymous)':
                new_response.type = 'additional'
            if responseCreator == task.Creator():
                new_response.type = 'clarification'
            #if util.getManagersVocab.getTerm(responseCreator):
            #   new_response.type =  'reply'
                   
            #check transition
            if data.get('transition'):
                wftool = getToolByName(self.context, 'portal_workflow')
                before = wftool.getInfoFor(self.context, 'review_state')
                if data.get('transition') != before:
                    before = wftool.getTitleForStateOnType(before, task.type)
                    wftool.doActionFor(self.context, data.get('transition'))
                    after = wftool.getInfoFor(self.context, 'review_state')
                    after = wftool.getTitleForStateOnType(after, task.type)
                    new_response.add_change('review_state', _(u'Issue state'),
                                        before, after)  

            #check other fields
            options = [(task.deadline, data.get('deadline'), 'deadline',  _('deadline')),(task.responsible, data.get('new_responsible'), 'responsible', _('responsible'))]
            for task_field, resp_field, option, title in options:
                if resp_field and task_field != resp_field:
                    new_response.add_change(option, title, task_field, resp_field)
                    task.__setattr__(option,resp_field)
            self.view.folder.add(new_response)
            self.request.RESPONSE.redirect(self.context.absolute_url())

class BeneathTask(grok.ViewletManager):
    grok.context(ITask)
    grok.name('ftw.task.beneathTask')

class ResponseView(grok.Viewlet, Base):
    grok.context(ITask)
    grok.name("ftw.task.response.view")
    grok.viewletmanager(BeneathTask)
    grok.order(1)

    def __init__(self, context, request, view, manager):
        grok.Viewlet.__init__(self,context,request,view, manager)
        Base.__init__(self,context, request)
    
        
class AddFormView(layout.FormWrapper, grok.Viewlet, Base):
    grok.implements(IResponseAdder)
    grok.context(ITask)
    grok.name("ftw.task.response.addForm")
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
     
     
class Create(Base):

    def determine_response_type(self, response):
        """Return a string indicating the type of response this is.
        """
        responseCreator = response.creator
        if responseCreator == '(anonymous)':
            return 'additional'

        issue = aq_inner(self.context)
        if responseCreator == issue.Creator():
            return 'clarification'

        if responseCreator in self.available_managers:
            return 'reply'

        # default:
        return 'additional'

    def __call__(self):
        update = {}
        form = self.request.form
        context = aq_inner(self.context)
        if not self.memship.checkPermission('Poi: Add Response', context):
            raise Unauthorized

        response_text = form.get('response', u'')
        new_response = Response(response_text)
        new_response.mimetype = self.mimetype
        new_response.type = self.determine_response_type(new_response)

        issue_has_changed = False
        transition = form.get('transition', u'')
        if transition and transition in self.available_transitions:
            wftool = getToolByName(context, 'portal_workflow')
            before = wftool.getInfoFor(context, 'review_state')
            before = wftool.getTitleForStateOnType(before, 'PoiIssue')
            wftool.doActionFor(context, transition)
            after = wftool.getInfoFor(context, 'review_state')
            after = wftool.getTitleForStateOnType(after, 'PoiIssue')
            new_response.add_change('review_state', _(u'Issue state'),
                                    before, after)
            issue_has_changed = True

        options = [
            ('severity', _(u'Severity'), 'available_severities'),
            ('responsibleManager', _(u'Responsible manager'),
             'available_managers'),
            ]
        # Changes that need to be applied to the issue (apart from
        # workflow changes that need to be handled separately).
        changes = {}
        for option, title, vocab in options:
            new = form.get(option, u'')
            if new and new in self.__getattribute__(vocab):
                current = self.__getattribute__(option)
                if current != new:
                    changes[option] = new
                    new_response.add_change(option, title,
                                            current, new)
                    issue_has_changed = True


        #('targetRelease', 'Target release', 'available_releases'),
        new = form.get('targetRelease', u'')
        if new and new in self.available_releases:
            current = self.targetRelease
            if current != new:
                # from value (uid) to key (id)
                new_label = self.available_releases.getValue(new)
                current_label = self.available_releases.getValue(current)
                changes['targetRelease'] = new
                new_response.add_change(option, _(u'Target release'),
                                        current_label, new_label)
                issue_has_changed = True

        attachment = form.get('attachment')
        if attachment:
            # File(id, title, file)
            data = File(attachment.filename, attachment.filename, attachment)
            new_response.attachment = data
            issue_has_changed = True

        if len(response_text) == 0 and not issue_has_changed:
            status = IStatusMessage(self.request)
            msg = _(u"No response text added and no issue changes made.")
            msg = translate(msg, 'Poi', context=self.request)
            status.addStatusMessage(msg, type='error')
        else:
            # Apply changes to issue
            context.update(**changes)
            # Add response
            self.folder.add(new_response)
        self.request.response.redirect(context.absolute_url())


class Edit(Base):

    @property
    @memoize
    def response(self):
        form = self.request.form
        context = aq_inner(self.context)
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
                    msg = translate(msg, 'Poi', context=context)
                    status.addStatusMessage(msg, type='info')
        self.request.response.redirect(context.absolute_url())


class Download(Base):
    """Download the attachment of a response.
    """

    def __call__(self):
        context = aq_inner(self.context)
        request = self.request
        response_id = self.validate_response_id()
        file = None
        if response_id != -1:
            response = self.folder[response_id]
            file = response.attachment
            if file is None:
                status = IStatusMessage(request)
                msg = _(u"Response id ${response_id} has no attachment.",
                        mapping=dict(response_id=response_id))
                msg = translate(msg, 'Poi', context=context)
                status.addStatusMessage(msg, type='error')
        if file is None:
            request.response.redirect(context.absolute_url())

        # From now on file exists.
        # Code mostly taken from Archetypes/Field.py:FileField.download
        filename = getattr(file, 'filename', file.getId())
        if filename is not None:
            if FILE_NORMALIZER:
                filename = IUserPreferredFileNameNormalizer(request).normalize(
                    safe_unicode(filename, context.getCharset()))
            else:
                filename = safe_unicode(filename, context.getCharset())
            header_value = contentDispositionHeader(
                disposition='attachment',
                filename=filename)
            request.response.setHeader("Content-disposition", header_value)
        return file.index_html(request, request.response)