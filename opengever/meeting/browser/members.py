from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.browser.modelforms import ModelAddForm
from opengever.base.browser.modelforms import ModelEditForm
from opengever.base.model import EMAIL_LENGTH
from opengever.base.model import FIRSTNAME_LENGTH
from opengever.base.model import LASTNAME_LENGTH
from opengever.meeting import _
from opengever.meeting.model import Member
from plone.supermodel import model
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import field
from zope import schema
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


class IMemberModel(model.Schema):
    """Member model schema interface."""

    firstname = schema.TextLine(
        title=_(u"label_firstname", default=u"Firstname"),
        max_length=FIRSTNAME_LENGTH,
        required=True)

    lastname = schema.TextLine(
        title=_(u"label_lastname", default=u"Lastname"),
        max_length=LASTNAME_LENGTH,
        required=True)

    email = schema.TextLine(
        title=_(u"label_email", default=u"E-Mail"),
        max_length=EMAIL_LENGTH,
        required=False)


class AddMember(ModelAddForm):

    schema = IMemberModel
    model_class = Member

    label = _('Add Member', default=u'Add Member')

    def nextURL(self):
        return '{}#members'.format(self.context.absolute_url())


class EditMember(ModelEditForm):

    fields = field.Fields(IMemberModel)

    def __init__(self, context, request):
        super(EditMember, self).__init__(context, request, context.model)

    def nextURL(self):
        return MemberView.url_for(aq_parent(aq_inner(self.context)),
                                  self.model)

    def prepare_model_tabs(self, viewlet):
        if not self.model.is_editable():
            return tuple()

        return viewlet.prepare_edit_tab(
            self.model.get_edit_url(self.context.parent), is_selected=True)


class MemberView(BrowserView):

    template = ViewPageTemplateFile('templates/member.pt')
    implements(IBrowserView, IPublishTraverse)

    @classmethod
    def url_for(cls, context, member):
        return member.get_url(context)

    def __init__(self, context, request):
        super(MemberView, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        return self.template()

    def can_edit_any_memberships(self):
        """Return whether the current user can edit any membership."""

        return any(self.can_edit_membership(membership)
                   for membership in self.model.memberships)

    def can_edit_membership(self, membership):
        """Return whether the current user can edit the membership."""

        return membership.is_editable_by_current_user(
            membership.committee.resolve_committee())

    def prepare_model_tabs(self, viewlet):
        if not self.model.is_editable():
            return tuple()

        return viewlet.prepare_edit_tab(
            self.model.get_edit_url(self.context.parent))
