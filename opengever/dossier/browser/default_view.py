from opengever.base.browser.default_view import OGDefaultView


class DossierDefaultView(OGDefaultView):
    """A customized default view for Dexterity content.

    On dossiers, we don't want to show the `public_trial`
    and `public_trial_statement` fields.
    """

    @property
    def omitted_fields(self):
        fields = ['IClassification.public_trial',
                  'IClassification.public_trial_statement']
        fields.extend(super(DossierDefaultView, self).omitted_fields)
        return fields
