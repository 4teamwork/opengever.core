from datetime import date
from datetime import datetime
from opengever.base.schema import TableChoice
from opengever.base.widgets import TrixFieldWidget
from plone.z3cform.layout import FormWrapper
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from zope import schema
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary
import json


class TestObject(object):
    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description


def get_radio_table_vocabulary():
    items = (
        TestObject(1, u'foo', 'Odi et amo.'),
        TestObject(2, u'bar', 'Quare id faciam fortasse requiris?'),
    )
    terms = []
    for each in items:
        terms.append(SimpleVocabulary.createTerm(each, each.id, each.title))
    return SimpleVocabulary(terms)


class IWidgetTestFormSchema(Interface):

    trix_field = schema.Text(title=u"trix_field", required=False)
    # field with default columns
    default_radio_table_field = TableChoice(
        required=False,
        title=u"default_table",
        show_filter=True,
        vocabulary=get_radio_table_vocabulary(),)
    # field with custom columns
    custom_radio_table_field = TableChoice(
        required=False,
        title=u"custom_table",
        vocabulary=get_radio_table_vocabulary(),
        columns=(
            {'column': 'description',
             'column_title': u'Description'},)
        )
    empty_radio_table_field = TableChoice(
        required=False,
        title=u"empty_table",
        vocabulary=SimpleVocabulary([]))


class WidgetTestForm(Form):
    ignoreContext = True
    fields = Fields(IWidgetTestFormSchema)

    def __init__(self, *args, **kwargs):
        super(WidgetTestForm, self).__init__(*args, **kwargs)
        self.result_data = None

    def update(self):
        self.fields['trix_field'].widgetFactory = TrixFieldWidget
        return super(WidgetTestForm, self).update()

    @buttonAndHandler(u'Submit')
    def handle_submit(self, action):
        data, errors = self.extractData()
        if len(errors) > 0:
            return

        self.result_data = {}
        for key, value in data.items():
            if not value:
                continue

            if isinstance(value, (datetime, date)):
                value = value.isoformat()

            if isinstance(value, TestObject):
                value = (value.id, value.title,)

            self.result_data[key] = value


class WidgetTestView(FormWrapper):
    form = WidgetTestForm

    def render(self):
        if self.form_instance.result_data:
            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            return json.dumps(self.form_instance.result_data)
        else:
            return super(WidgetTestView, self).render()
