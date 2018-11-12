from contextlib import contextmanager
from datetime import date
from datetime import datetime
from dateutil.parser import parse as date_parser
from ftw.upgrade import UpgradeStep
from opengever.bundle.sections.constructor import BUNDLE_GUID_KEY
from opengever.ech0147.interfaces import IECH0147Settings
from plone import api
from plone.dexterity.utils import iterSchemata
from pyxb.binding.datatypes import boolean as pyxb_boolean
from pyxb.binding.datatypes import date as pyxb_date
from pyxb.binding.datatypes import dateTime as pyxb_datetime
from pyxb.binding.datatypes import int as pyxb_int
from pyxb.binding.datatypes import string as pyxb_string
from zope.annotation import IAnnotations
from zope.schema import getFieldsInOrder
import logging
import pyxb.binding.datatypes


logger = logging.getLogger("opengever.core")


@contextmanager
def writable(field):
    try:
        original_readonly = field.readonly
        field.readonly = False
        yield field
    finally:
        field.readonly = original_readonly


class EnsureAllFieldsOfECH0147ImportedObjectsAreProperlyTyped(UpgradeStep):
    """Ensure all fields of eCH-0147 imported objects are properly typed.
    """
    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()

        # Skip if eCH-0147 imports are not enabled
        if not api.portal.get_registry_record("ech0147_import_enabled", interface=IECH0147Settings):
            return

        # Only query non-imported-from-bundle documents and dossiers
        affected_types = ("opengever.dossier.businesscasedossier", "opengever.document.document")
        query = {"portal_type": affected_types, "bundle_guid": None}
        primitive_pyxb_types = pyxb.binding.datatypes.__dict__.get("_PrimitiveDatatypes")
        trivial_pyxb_types = (pyxb_int, pyxb_boolean, pyxb_string)
        trivial_types = (int, basestring)

        for obj in self.objects(query, "Ensure all fields of eCH-0147 imported objects are properly typed."):
            # Skip imported-from-bundle objects not on the index
            if IAnnotations(obj).get(BUNDLE_GUID_KEY):
                continue
            for schema in iterSchemata(obj):
                for name, field in getFieldsInOrder(schema):
                    value = getattr(field.interface(obj), name, None)
                    value_type = type(value)
                    # Only touch pyxb typed values
                    if field._type and value is not None and isinstance(value_type, primitive_pyxb_types):
                        object_path = "/".join(obj.getPhysicalPath())
                        logger.info(
                            "Found PyXB values in object %s field %s field type %s value type %s.",
                            object_path,
                            name,
                            repr(field._type),
                            repr(value_type),
                        )
                        if isinstance(value_type, trivial_pyxb_types) and field._type in trivial_types:
                            with writable(field) as wfield:
                                wfield.set(wfield.interface(obj), wfield._type(value))
                        elif isinstance(value_type, pyxb_date) and field._type is date:
                            with writable(field) as wfield:
                                wfield.set(wfield.interface(obj), wfield._type.fromordinal(wfield.toordinal()))
                        elif isinstance(value_type, pyxb_datetime) and field._type is datetime:
                            with writable(field) as wfield:
                                wfield.set(wfield.interface(obj), date_parser(value.ISO()))
                        else:
                            logger.warn(
                                "PyXB values in object %s field %s field type %s value type %s fell through!",
                                object_path,
                                name,
                                repr(field._type),
                                repr(value_type),
                            )
