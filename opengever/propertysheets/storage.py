from opengever.propertysheets.assignment import get_slots_enforcing_unique_field_names
from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.propertysheets.exceptions import InvalidSchemaAssignment
from persistent.mapping import PersistentMapping
from plone import api
from zope.annotation import IAnnotations


class PropertySheetSchemaStorage(object):
    """Handle storage and lookup of property sheets.

    Property sheets are stored in the annotation of the plone site.
    """
    ANNOTATIONS_KEY = 'opengever.propertysheets.schema_definitions'

    def __init__(self):
        self.context = api.portal.get()

    def __contains__(self, name):
        annotations = IAnnotations(self.context)
        storage = annotations.get(self.ANNOTATIONS_KEY, {})

        return name in storage

    def __len__(self):
        annotations = IAnnotations(self.context)
        return len(annotations.get(self.ANNOTATIONS_KEY, {}))

    def __nonzero__(self):
        return bool(len(self))

    def list(self):
        annotations = IAnnotations(self.context)

        result = []
        for name in annotations.get(self.ANNOTATIONS_KEY, {}):
            result.append(self.get(name))
        return result

    def _validate_schema_definition(self, storage, new_definition):
        """Validate a new schema definition.

        Performs the following validations:
        - Ensure that there is at most one definition per slot.
        - Ensure that a definition is not assigned to conflicting slots.
        - Ensure that fields within the schema definitions do not overlap.
          Currently an external method defines the relationship between
          different slots and which slots could overlap other slots.

        """
        used_assignments = set()
        for definition_data in storage.values():
            used_assignments.update(definition_data['assignments'])

        for new_assignment in new_definition.assignments:
            if new_assignment in used_assignments:
                raise InvalidSchemaAssignment(
                    u"The assignment '{}' is already in use.".format(
                        new_assignment)
                )
            used_assignments.add(new_assignment)

        maybe_conflicting = set()
        for slot_name in new_definition.assignments:
            maybe_conflicting.update(
                get_slots_enforcing_unique_field_names(slot_name)
            )

        conflicting_within_new_definition = [
            assignment for assignment in new_definition.assignments
            if assignment in maybe_conflicting
        ]
        if conflicting_within_new_definition:
            raise InvalidSchemaAssignment(
                u"The assignments '{}' cannot be used for the same "
                u"sheet.".format(
                    u"', '".join(conflicting_within_new_definition))
            )

        # sort for stable validation order/output
        for assignment in sorted(maybe_conflicting):
            existing_definition = self.query(assignment)
            if not existing_definition:
                continue

            intersecting_fields = (
                set(existing_definition.get_fieldnames())
                & set(new_definition.get_fieldnames())
            )
            if intersecting_fields:
                raise InvalidSchemaAssignment(
                    u"Overlapping field names '{}' in assignment '{}'".format(
                        u"', '".join(intersecting_fields), assignment
                    )
                )

    def save(self, schema_definition):
        annotations = IAnnotations(self.context)
        if self.ANNOTATIONS_KEY not in annotations:
            annotations[self.ANNOTATIONS_KEY] = PersistentMapping()
        storage = annotations[self.ANNOTATIONS_KEY]

        self._validate_schema_definition(storage, schema_definition)

        schema_definition._save(storage)

    def get(self, name):
        annotations = IAnnotations(self.context)
        storage = annotations.get(self.ANNOTATIONS_KEY, {})

        if name not in storage:
            return None

        return PropertySheetSchemaDefinition._load(storage, name)

    def query(self, assignment_slot_name):
        annotations = IAnnotations(self.context)
        storage = annotations.get(self.ANNOTATIONS_KEY, {})
        for name, definition_data in storage.items():
            if assignment_slot_name in definition_data['assignments']:
                return self.get(name)

        return None

    def remove(self, name):
        annotations = IAnnotations(self.context)
        storage = annotations.get(self.ANNOTATIONS_KEY, {})
        storage.pop(name, None)

    def clear(self):
        annotations = IAnnotations(self.context)
        annotations.pop(self.ANNOTATIONS_KEY, None)
