from opengever.base.browser.modelforms import ModelAddForm
from opengever.base.browser.modelforms import ModelEditForm
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact import _
from opengever.contact.models.person import Person
from opengever.ogds.models import FIRSTNAME_LENGTH
from opengever.ogds.models import LASTNAME_LENGTH
from plone.directives import form
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import field
from zope import schema
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


"""
TODO FOR THIS PR:

- Move Footer to EMAIL_TEMPLATE to toggle with editEnabled var and not with css
- remove editable class in plonetheme.teamraum after Footer is moved to EMAIL_TEMPLATE
- add more stylings
- remove implementation in person_edit.pt
"""

EMAIL_TEMPLATE = '''
<script id="emailTemplate" type="text/x-handlebars-template">
  <h4>
    <span i18n:translate="label_mail">Mail Addresses</span>
    {{#unless editEnabled}}
        <a class="toggle-edit-email fa-pencil edit-link action" />
    {{/unless}}
    {{#if editEnabled}}
        <a class="toggle-edit-email fa-check edit-link action" />
        <a class="abort-edit-email fa-times abort-link action" />
    {{/if}}
  </h4>
  <ul class="form-list" tal:attributes="data-fetch-url view/get_fetch_url">
      {{#each mailaddresses}}
        <li>
        {{#if ../editEnabled}}
            <input class="update-label" type="text" value={{label}} />
            <input class="update-address" type="text" value={{address}} />
            <span class="button-group">
                <a data-delete-url="{{delete_url}}" class="remove-email fa fa-trash"></a>
            </span>
        {{else}}
            <span class="label">{{label}}</span>
            <span class="address">{{address}}</span>
        {{/if}}
        </li>
      {{/each}}

      {{#if editEnabled}}
        <li>
          <input id="email-label" type="text" name="label" />
          <input id="email-mailaddress" type="email" name="email" />
          <span class="button-group">
            <a class="button add-email fa fa-plus" tal:attributes="data-create-url view/get_create_mail_url"></a>
        </li>
      {{/if}}
   </ul>
</script>
'''


class PersonView(BrowserView):
    """Overview for a Person SQL object.
    """

    implements(IBrowserView, IPublishTraverse)

    template = ViewPageTemplateFile('templates/person.pt')

    def __init__(self, context, request):
        super(PersonView, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        return self.template()

    def prepare_model_tabs(self, viewlet):
        if not self.model.is_editable():
            return tuple()

        return viewlet.prepare_edit_tab(
            self.model.get_edit_url(self.context.parent))

    def get_fetch_url(self):
        return self.context.model.get_url('mails/list')

    def get_create_mail_url(self):
        return self.context.model.get_url('mails/add')

    def render_handlebars_email_template(self):
        return EMAIL_TEMPLATE


class IPersonModel(form.Schema):
    """Person model schema interface."""

    salutation = schema.TextLine(
        title=_(u"label_salutation", default=u"Salutation"),
        max_length=CONTENT_TITLE_LENGTH,
        required=False)

    academic_title = schema.TextLine(
        title=_(u"label_academic_title", default=u"Academic title"),
        max_length=CONTENT_TITLE_LENGTH,
        required=False)

    firstname = schema.TextLine(
        title=_(u"label_firstname", default=u"Firstname"),
        max_length=FIRSTNAME_LENGTH,
        required=True)

    lastname = schema.TextLine(
        title=_(u"label_lastname", default=u"Lastname"),
        max_length=LASTNAME_LENGTH,
        required=True)

    description = schema.Text(
        title=_(u'label_description', default=u'Description'),
        required=False,
        missing_value=u'',
        default=u'',
        )


class AddPerson(ModelAddForm):
    schema = IPersonModel
    model_class = Person

    label = _('Add Person', default=u'Add Person')

    def nextURL(self):
        return self._created_object.get_url()


class EditPerson(ModelEditForm):

    fields = field.Fields(IPersonModel)
    template = ViewPageTemplateFile('templates/person_edit.pt')

    def __init__(self, context, request):
        super(EditPerson, self).__init__(context, request, context.model)

    def nextURL(self):
        return self.context.model.get_url()

    def prepare_model_tabs(self, viewlet):
        if not self.model.is_editable():
            return tuple()

        return viewlet.prepare_edit_tab(
            self.model.get_edit_url(self.context.parent), is_selected=True)
