from datetime import date
from datetime import datetime
from opengever.base.widgets import TrixFieldWidget
from plone.z3cform.layout import FormWrapper
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from zope import schema
from zope.interface import Interface
import json


class IWidgetTestFormSchema(Interface):

    trix_field = schema.Text(title=u"trix_field", required=False)


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

            self.result_data[key] = value


class WidgetTestView(FormWrapper):
    form = WidgetTestForm

    def render(self):
        if self.form_instance.result_data:
            self.request.RESPONSE.setHeader('Content-Type', 'application/json')
            return json.dumps(self.form_instance.result_data)
        else:
            return super(WidgetTestView, self).render()
