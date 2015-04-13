from five import grok
from opengever.meeting import _
from opengever.meeting.form import ModelAddForm
from opengever.meeting.form import ModelEditForm
from opengever.meeting.model import Member
from plone.directives import form
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import field
from zExceptions import NotFound
from zope import schema
from zope.interface import implements
from zope.interface import Interface
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

    label = _('Add Member', default=u'Add Member')

    def nextURL(self):
        return MemberView.url_for(self.context, self._created_object)


class EditMember(ModelEditForm):

    fields = field.Fields(IMemberModel)

    def nextURL(self):
        return MemberView.url_for(self.context, self.model)


class MemberTraverser(grok.View):

    implements(IPublishTraverse)
    grok.context(Interface)
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
