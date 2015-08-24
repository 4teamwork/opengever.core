from plone.formwidget.autocomplete.widget import AutocompleteMultiFieldWidget
from plone.z3cform.layout import FormWrapper
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.formwidget.query.interfaces import IQuerySource
from zope import schema
from zope.interface import implements
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import json


class TestUsersVocabulary(SimpleVocabulary):
    implements(IVocabularyFactory, IQuerySource)

    def __init__(self):
        super(TestUsersVocabulary, self).__init__([
            SimpleTerm(u'james', u'james', u'James Bond'),
            SimpleTerm(u'hans', u'hans', u'Hans M\xfcller'),
            SimpleTerm(u'hugo', u'hugo', u'Hugo Boss')])

    def search(self, query_string):
        query_string = query_string.lower()
        for term in self():
            if query_string in term.title.lower():
                yield term

    def __call__(self, context=None):
        return self


class IUserSelectionFormSchema(Interface):

    users = schema.List(
        title=u'Select users',
        value_type=schema.Choice(
            vocabulary='test-users-vocabulary'),
        required=False)


class UserSelectionForm(Form):
    label = u'Select users'
    ignoreContext = True
    fields = Fields(IUserSelectionFormSchema)

    def __init__(self, *args, **kwargs):
        super(UserSelectionForm, self).__init__(*args, **kwargs)
        self.result_data = None

    def update(self):
        self.fields['users'].widgetFactory = AutocompleteMultiFieldWidget
        return super(UserSelectionForm, self).update()

    @buttonAndHandler(u'Submit')
    def handle_submit(self, action):
        data, errors = self.extractData()
        if len(errors) > 0:
            return

        self.result_data = {}
        for key, value in data.items():
            if not value:
                continue

            self.result_data[key] = value


class UserSelectionView(FormWrapper):

    form = UserSelectionForm

    def render(self):
        if self.form_instance.result_data:
            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            return json.dumps(self.form_instance.result_data)
        else:
            return super(UserSelectionView, self).render()
