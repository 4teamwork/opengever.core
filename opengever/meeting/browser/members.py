from five import grok
from opengever.meeting import _
from opengever.meeting.committeecontainer import ICommitteeContainer
from opengever.meeting.form import ModelAddForm
from opengever.meeting.model import Member
from plone.directives import form
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form import field
from z3c.form.form import EditForm
from zExceptions import NotFound
from zope import schema
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


class IMemberModel(form.Schema):
    """Member model schema interface."""

    firstname = schema.TextLine(
        title=_(u"label_firstname", default=u"Firstname"),
        max_length=256,
        required=True)

    lastname = schema.TextLine(
        title=_(u"label_lastname", default=u"Lastname"),
        max_length=256,
        required=True)

    email = schema.TextLine(
        title=_(u"label_email", default=u"E-Mail"),
        max_length=256,
        required=False)


class AddMember(ModelAddForm):

    schema = IMemberModel
    model_class = Member


class EditMember(EditForm):

    ignoreContext = True
    fields = field.Fields(IMemberModel)

    is_model_view = True
    is_model_edit_view = True

    def __init__(self, context, request, model):
        super(EditMember, self).__init__(context, request)
        self.model = model
        self._has_finished_edit = False

    def inject_initial_data(self):
        if self.request.method != 'GET':
            return

        prefix = 'form.widgets.'
        values = self.model.get_edit_values(self.fields.keys())

        for fieldname, value in values.items():
            self.request[prefix + fieldname] = value

    def updateWidgets(self):
        self.inject_initial_data()
        super(EditMember, self).updateWidgets()

    def applyChanges(self, data):
        self.model.update_model(data)
        # pretend to always change the underlying data
        self._has_finished_edit = True
        return True

    # this renames the button but otherwise preserves super's behavior
    @button.buttonAndHandler(_('Save'), name='save')
    def handleApply(self, action):
        # self as first argument is required by the decorator
        super(EditMember, self).handleApply(self, action)

    def nextURL(self):
        return MemberView.url_for(self.context, self.model)

    def render(self):
        if self._has_finished_edit:
            return self.request.response.redirect(self.nextURL())
        return super(EditMember, self).render()


class MemberList(grok.View):

    implements(IPublishTraverse)
    grok.context(ICommitteeContainer)
    grok.name('member')

    @classmethod
    def url_for(cls, context):
        return "{}/{}".format(
            context.absolute_url(), cls.__view_name__)

    def render(self):
        """This view is never rendered directly.

        This method ist still needed to make grok checks happy, every grokked
        view must have an associated template or 'render' method.

        """
        pass

    def publishTraverse(self, request, name):
        try:
            member_id = int(name)
        except ValueError:
            raise NotFound

        member = Member.query.get(member_id)
        if member is None:
            raise NotFound

        return MemberView(self.context, self.request, member)


class MemberView(BrowserView):

    template = ViewPageTemplateFile('members_templates/member.pt')
    implements(IBrowserView, IPublishTraverse)

    is_model_view = True
    is_model_edit_view = False

    mapped_actions = {
        'edit': EditMember,
    }

    @classmethod
    def url_for(cls, context, member):
        return "{}/member/{}".format(
            context.absolute_url(), member.member_id)

    def __init__(self, context, request, member):
        super(MemberView, self).__init__(context, request)
        self.model = member

    def __call__(self):
        return self.template()

    def publishTraverse(self, request, name):
        if name in self.mapped_actions:
            view_class = self.mapped_actions.get(name)
            return view_class(self.context, self.request, self.model)
        raise NotFound
