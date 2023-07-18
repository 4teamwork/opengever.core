from opengever.base.monkey.patching import MonkeyPatch


class PatchRestAPICreateForm(MonkeyPatch):
    """Monkey patch plone.restapi's create_form so that it supports
    also a display mode.
    """

    def __call__(self):
        from plone.autoform.form import AutoExtensibleForm
        from z3c.form import form as z3c_form
        from z3c.form.interfaces import DISPLAY_MODE

        def create_form(context, request, base_schema, additional_schemata=None):
            """Create a minimal, standalone z3c form and run the field processing
            logic of plone.autoform on it.
            """
            if additional_schemata is None:
                additional_schemata = ()

            class SchemaForm(AutoExtensibleForm, z3c_form.AddForm):
                schema = base_schema
                additionalSchemata = additional_schemata
                ignoreContext = True

            form = SchemaForm(context, request)
            if request.get('mode') == 'display':
                form.mode = DISPLAY_MODE

            form.updateFieldsFromSchemata()
            return form

        from plone.restapi.types import utils
        self.patch_refs(
            utils, 'create_form', create_form)
