from plone import api
from plone.dexterity.i18n import MessageFactory as pd_mf
from plone.z3cform.layout import FormWrapper
from zope.component import queryMultiAdapter


class WizzardWrappedAddForm(FormWrapper):

    typename = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

        ttool = api.portal.get_tool('portal_types')
        self.fti = ttool.getTypeInfo(self.typename)

        FormWrapper.__init__(self, context, request)

        # Set portal_type name on newly created form instance
        if self.form_instance is not None and \
                not getattr(self.form_instance, 'portal_type', None):
            self.form_instance.portal_type = self.fti.getId()

    @property
    def form(self):
        """
        This form wraps another add form into the wizard. It is
        important that the original add form is used, since there
        may be custom things like hidden widgets in updateWidgets(). There
        are also several ways how a dexterity add form can be customized.
        Therefore we just get the original add form from the add-view and
        wrap it with our wizard stuff. See _wrap_form.

        """
        if getattr(self, '_form', None) is not None:
            return self._form

        add_view = queryMultiAdapter((self.context, self.request, self.fti),
                                     name=self.fti.factory)
        if add_view is None:
            add_view = queryMultiAdapter((self.context, self.request,
                                          self.fti))

        self._form = self._wrap_form(add_view.form)

        return self._form

    def _wrap_form(self, parent_form_class):
        """
        The original form is passed as `parent_form_class` here and is
        "extended" with the wizard stuff (different template, passing of
        values from earlier steps, step configuration etc.). This is done by
        subclassing the original form and overwriting the buttons, since
        we need to do our custom stuff.

        """
        steptitle = pd_mf(u'Add ${name}',
                          mapping={'name': self.fti.Title()})

        form_class = self._create_form_class(parent_form_class, steptitle)

        form_class.__name__ = 'WizardForm: %s' % parent_form_class.__name__
        return form_class

    def _create_form_class(self, parent_form_class, steptitle):
        """Create a custom form class here, e.g.:

        class WrappedForm(BaseWizardStepForm, parent_form_class):
            step_name = 'add-some-type'
            step_title = steptitle
            steps = the_stepd

            @buttonAndHandler(pd_mf(u'Save'), name='save')
            def handleAdd(self, action):
                data, errors = self.extractData()
                if errors:
                    self.status = self.formErrorsMessage
                    return

                # crate content type here
                # ...

                return self.request.RESPONSE.redirect('somewhere')

            @buttonAndHandler(pd_mf(u'Cancel'), name='cancel')
            def handleCancel(self, action):
                return self.request.RESPONSE.redirect('somewhere_else')

        return WrappedForm

        """
        raise NotImplementedError()
