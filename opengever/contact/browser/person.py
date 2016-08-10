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
- refactoring js
- handle validation
- refresh after safe form does not work properly (needs a manual page refresh to see changes)
"""

FORM_TOGGLER_PARTIAL = '''
<script id="form-toggler-partial" type="text/x-handlebars-template">
    {{#unless editEnabled}}
        <a class="show-edit-form fa-pencil action" />
    {{/unless}}
    {{#if editEnabled}}
        <a class="save-edit-form fa-check action" />
        <a class="abort-edit-form fa-times action" />
    {{/if}}
</script>
'''

EMAIL_TEMPLATE = '''
<script id="email-edit-row" type="text/x-handlebars-template">
  <li class="editableRow" data-id="{{id}}"
                          data-action="update"
                          data-update-url="{{update_url}}"
                          data-delete-url="{{delete_url}}">
      <div class="validation-error" />
      <input type="text" name="label" value="{{label}}" />
      <input type="email" name="email" value="{{address}}" />
      <a class="remove-row action fa fa-trash"></a>
  </li>
</script>
<script id="emailTemplate" type="text/x-handlebars-template">
  <h4>
    <span i18n:translate="label_mail">Mail Addresses</span>
    {{> form-toggler-partial}}
  </h4>
  <ul class="form-list">
      {{#each mailaddresses}}
        {{#if ../editEnabled}}
          {{> email-edit-row}}
        {{else}}
          <li>
            <span class="label">{{label}}</span>
            <span class="address">{{address}}</span>
          </li>
        {{/if}}
        </li>
      {{/each}}
   </ul>
   {{#if editEnabled}}
       <a class="add-row fa-plus action"></>
   {{/if}}
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

    def get_create_url(self):
        return self.context.model.get_url('mails/add')

    def get_set_all_url(self):
        return self.context.model.get_url('mails/set_all')

    def get_validate_url(self):
        return self.context.model.get_url('mails/validate')

    def render_handlebars_email_template(self):
        return EMAIL_TEMPLATE

    def render_handlebars_form_toggler_partial(self):
        return FORM_TOGGLER_PARTIAL


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
