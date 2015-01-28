from five import grok
from opengever.base.model import create_session
from opengever.meeting import _
from opengever.meeting.committeecontainer import ICommitteeContainer
from opengever.meeting.model import Member
from plone.autoform.form import AutoExtensibleForm
from plone.directives import form
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.form import AddForm
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


class AddMember(AutoExtensibleForm, AddForm):

    ignoreContext = True
    schema = IMemberModel

    def __init__(self, context, request):
        super(AddMember, self).__init__(context, request)
        self._created_object = None

    def create(self, data):
        return Member(**data)

    def add(self, obj):
        session = create_session()
        session.add(obj)
        session.flush()  # required to create an autoincremented id
        self._created_object = obj

    def nextURL(self):
        return self.context.absolute_url()


class MemberList(grok.View):

    implements(IPublishTraverse)
    grok.context(ICommitteeContainer)
    grok.name('member')
    grok.template('members')

    mapped_actions = {
        'add-member': AddMember,
    }

    @classmethod
    def url_for(cls, context):
        return "{}/{}".format(
            context.absolute_url(), cls.__view_name__)

    def members(self):
        return Member.query

    def member_url(self, member):
        return MemberView.url_for(self.context, member)

    def publishTraverse(self, request, name):
        if name in self.mapped_actions:
            view_class = self.mapped_actions.get(name)
            return view_class(self.context, self.request)

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

    @classmethod
    def url_for(cls, context, member):
        return "{}/member/{}".format(
            context.absolute_url(), member.member_id)

    def __init__(self, context, request, member):
        super(MemberView, self).__init__(context, request)
        self.model = member

    def __call__(self):
        return self.template()
