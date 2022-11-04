from plone.dexterity.utils import safe_utf8
from zope.schema import Choice
from zope.schema import Set


def is_choice_field(field):
    return isinstance(field, Choice)


def is_multiple_choice_field(field):
    return isinstance(field, Set) and isinstance(field.value_type, Choice)


def _add_value_to_vocabulary(vocab, value):
    term = vocab.createTerm(safe_utf8(value))
    vocab._terms.append(term)
    vocab.by_value[term.value] = term
    vocab.by_token[term.value] = term


def add_current_value_to_allowed_terms(field, context):
    from opengever.propertysheets.utils import get_custom_properties
    current_value = get_custom_properties(context).get(field.getName())
    if not current_value:
        return
    if is_choice_field(field):
        _add_value_to_vocabulary(field.vocabulary, current_value)
    elif is_multiple_choice_field(field):
        vocab = field.value_type.vocabulary
        for value in current_value:
            if value not in vocab:
                _add_value_to_vocabulary(vocab, value)
