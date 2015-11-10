from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.meeting import _
from opengever.meeting.form import ModelAddForm
from opengever.meeting.form import ModelEditForm
from opengever.meeting.model import Member
from opengever.ogds.models import EMAIL_LENGTH
from opengever.ogds.models import FIRSTNAME_LENGTH
from opengever.ogds.models import LASTNAME_LENGTH
from plone.directives import form
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import field
from zope import schema
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


class IMemberModel(form.Schema):
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
        return MemberView.url_for(self.context, self._created_object)


class EditMember(ModelEditForm):

    fields = field.Fields(IMemberModel)

    def __init__(self, context, request):
        super(EditMember, self).__init__(context, request, context.model)

    def nextURL(self):
        return MemberView.url_for(aq_parent(aq_inner(self.context)),
                                  self.model)


class MemberView(BrowserView):

    template = ViewPageTemplateFile('templates/member.pt')
    implements(IBrowserView, IPublishTraverse)

    has_model_breadcrumbs = True
    is_model_view = True
    is_model_edit_view = False

    @classmethod
    def url_for(cls, context, member):
        return member.get_url(context)

    def __init__(self, context, request):
        super(MemberView, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        return self.template()
