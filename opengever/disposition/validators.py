from opengever.disposition import _
from opengever.disposition.disposition import IDispositionSchema
from opengever.disposition.interfaces import IDisposition
from opengever.disposition.interfaces import IDispositionSettings
from plone import api
from plone.memoize.instance import memoize
from z3c.form import validator
from zope.interface import Invalid


class OfferedDossiersValidator(validator.SimpleFieldValidator):

    _current_dossiers = None

    @property
    @memoize
    def disregard_retention_period(self):
        return api.portal.get_registry_record(
            name='disregard_retention_period', interface=IDispositionSettings)

    def validate(self, value):
        """Validate if the retention period of all selected dossiers is
        expired and the dossiers are not part of another disposition.
        """
        for dossier in value:
            if not self.is_retention_period_expired(dossier):
                raise Invalid(
                    _(u'error_retention_period_not_expired',
                      default=u'The retention period of the selected '
                              'dossiers is not expired.'))

            if self.is_offered_in_a_different_disposition(dossier):
                raise Invalid(
                    _(u'error_offered_in_a_different_disposition',
                      default=u'The dossier ${title} is already offered in a '
                      'different disposition.',
                      mapping={'title': dossier.title}))

        return super(OfferedDossiersValidator, self).validate(value)
    def is_retention_period_expired(self, dossier):
        if self.disregard_retention_period:
            return True

        return dossier.is_retention_period_expired()

    def is_offered_in_a_different_disposition(self, dossier):
        if api.content.get_state(dossier) == 'dossier-state-offered':
            return dossier not in self.get_current_dossiers()

        return False

    def get_current_dossiers(self):
        if not self._current_dossiers:
            if IDisposition.providedBy(self.context):
                self._current_dossiers = [
                    relation.to_object for relation in self.context.dossiers]
            else:
                # disposition AddForm
                self._current_dossiers = []

        return self._current_dossiers


validator.WidgetValidatorDiscriminators(
    OfferedDossiersValidator,
    field=IDispositionSchema['dossiers'],
)
