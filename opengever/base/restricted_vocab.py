from opengever.base.acquisition import acquire_field_value
from Products.CMFCore.interfaces import ISiteRoot
from opengever.base.acquisition import NO_VALUE_FOUND
from opengever.base.interfaces import IDuringContentCreation
from plone.app.dexterity.behaviors.metadata import MetadataBase
from Products.CMFPlone.utils import safe_callable
import zope.schema.vocabulary


class RestrictedVocabularyFactory(object):
    """Factory for a restricted vocabulary.

    Expects a `choices` list which looks as follows:
    choices = (
    (0,     u'none'),
    (1,     u'raw_choice_one'),
    (1,     u'raw_choice_two'),
    (2,     u'detailed_choice_one'),
    (2,     u'detailed_choice_two'),
    )

    Use the string as internationalization message-id.

    Alternatively, `choices` can be a callable that produces such a list.

    What it does in the example:
    if the parent object has a "raw" choice set, then only detailed
    choices or the selected raw choice are allowed to be selected.

    `restricted` can be a boolean or a callable (with no arguments) that
    returns a boolean, indicating whether the vocabulary should be restricted
    or not.
    """

    def __init__(self, field, choices, message_factory, restricted=True):
        self.field = field
        self._choices = choices
        self.message_factory = message_factory
        self._restricted = restricted

    @property
    def restricted(self):
        if safe_callable(self._restricted):
            return self._restricted()
        return self._restricted

    @property
    def choice_level_mapping(self):
        choice_level_mapping = [list(a) for a in self.choices[:]]
        choice_level_mapping = dict([a for a in choice_level_mapping
                                     if not a.reverse()])
        return choice_level_mapping

    @property
    def choice_names(self):
        return [a[1] for a in self.choices]

    @property
    def choices(self):
        if safe_callable(self._choices):
            return self._choices()
        return self._choices

    def __call__(self, context):
        terms = []
        for name in self.get_allowed_choice_names(context):
            title = name
            if self.message_factory:
                title = self.message_factory(name)
            terms.append(
                zope.schema.vocabulary.SimpleTerm(name, title=title))
        return zope.schema.vocabulary.SimpleVocabulary(terms)

    def get_allowed_choice_names(self, context):
        acquired_value = self._acquire_value(context)

        if not self.restricted:
            return self.choice_names

        if not acquired_value or acquired_value not in self.choice_names:
            # XXX: Compare against sentinel value (Issue #2030)
            return self.choice_names

        allowed_choice_names = []
        allowed_choice_names.append(acquired_value)
        allowed_level = self.choice_level_mapping[acquired_value] + 1
        for level, name in self.choices:
            if level >= allowed_level:
                allowed_choice_names.append(name)

        return allowed_choice_names

    def _acquire_value(self, context):
        if isinstance(context, MetadataBase) or context is None:
            # we do not test the factory, it is not acquisition wrapped and
            # we cant get the request...
            return None

        request = context.REQUEST
        if IDuringContentCreation.providedBy(request):
            # object does not yet exist, context is container (add)
            container = context
        elif ISiteRoot.providedBy(context):
            # The context is the siteroot when using the /@types endpoint
            # from the plone rest-api.
            # See https://github.com/4teamwork/opengever.core/issues/5283
            container = context
        else:
            # object already exists, container is parent of context (edit)
            container = context.aq_inner.aq_parent

        acquired_value = acquire_field_value(self.field, container)

        # Use acquired value if one was found
        if acquired_value is not NO_VALUE_FOUND:
            return acquired_value

        # Otherwise fall back to static field default
        #
        # NOTE: We deliberately avoid accessing field.default, because doing
        # so would invoke a defaultFactory if present
        return self.field.__dict__.get('default', None)


def propagate_vocab_restrictions(container, event, restricted_fields, marker):
    """Propagate changes to fields with restricted vocabularies down to
    children of the folderish object (for the children whose field value would
    now violate the business rule imposed by the restricted vocabulary).
    """
    def dottedname(field):
        return '.'.join((field.interface.__name__, field.__name__))

    changed_fields = []
    for desc in event.descriptions:
        for name in desc.attributes:
            changed_fields.append(name)

    fields_to_check = []
    for field in restricted_fields:
        if dottedname(field) in changed_fields:
            fields_to_check.append(field)

    if not fields_to_check:
        return

    children = container.portal_catalog(
        # XXX: Depth should not be limited (Issue #2027)
        path={'depth': 2,
              'query': '/'.join(container.getPhysicalPath())},
        object_provides=(marker.__identifier__,)
    )

    for child in children:
        obj = child.getObject()
        for field in fields_to_check:
            voc = field.bind(obj).source
            value = field.get(field.interface(obj))
            if value not in voc:
                # Change the child object's field value to a valid one
                # acquired from above
                new_value = acquire_field_value(field, obj.aq_parent)
                field.set(field.interface(obj), new_value)
