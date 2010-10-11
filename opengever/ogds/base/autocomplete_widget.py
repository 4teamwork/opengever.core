
from zope.interface import implementer
from zope.component import getUtility
from zope.schema.interfaces import ISource
from zope.schema.interfaces import IContextSourceBinder

from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget

from plone.formwidget.autocomplete import widget
from collective.elephantvocabulary.interfaces import IElephantVocabulary

from opengever.ogds.base.interfaces import IContactInformation


class AutocompleteSelectionWidget(widget.AutocompleteSelectionWidget):

    @property
    def bound_source(self):
        if self._bound_source is None:
            source = self.source
            if IContextSourceBinder.providedBy(source):
                source = source(self.context)
            assert ISource.providedBy(source)

            # custom
            if IElephantVocabulary.providedBy(source) and \
                    self.field.interface.providedBy(self.context):
                value = getattr(self.field.interface(self.context),
                                self.field.__name__)
                if value and value not in source.vocab:
                    contact_info = getUtility(IContactInformation)
                    term = source.vocab.createTerm(value, value,
                            contact_info.describe(value))
                    source.vocab._terms.append(term)
                    source.vocab.by_value[term.value] = term
                    source.vocab.by_token[term.token] = term
                    source.hidden_terms.append(value)
            # end custom
            self._bound_source = source
        return self._bound_source


@implementer(IFieldWidget)
def AutocompleteFieldWidget(field, request):
    return FieldWidget(field,
                AutocompleteSelectionWidget(request))
