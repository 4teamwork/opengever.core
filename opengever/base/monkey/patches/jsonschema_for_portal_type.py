from opengever.base.behaviors.translated_title import get_inactive_languages
from opengever.base.behaviors.translated_title import has_translation_behavior
from opengever.base.monkey.patching import MonkeyPatch
from plone.restapi.types import utils
from Products.CMFCore.utils import getToolByName


class PatchGetJsonschemaForPortalType(MonkeyPatch):
    def __call__(self):
        original_get_jsonschema_for_portal_type = utils.get_jsonschema_for_portal_type

        def get_jsonschema_for_portal_type(portal_type, context, request, excluded_fields=None):
            excluded_fields = list(excluded_fields or [])

            ttool = getToolByName(context, "portal_types")
            fti = ttool[portal_type]

            if has_translation_behavior(fti):
                for lang in get_inactive_languages():
                    fieldname = 'title_{}'.format(lang)
                    excluded_fields.append(fieldname)

            schema = original_get_jsonschema_for_portal_type(
                portal_type, context, request, excluded_fields=excluded_fields)

            # exclude only excludes from some parts. sanitize output before
            # returning the schema.
            for field in excluded_fields:
                if schema.get('required') and field in schema['required']:
                    schema['required'].remove(field)
                for fieldset in schema.get('fieldsets', []):
                    if field in fieldset.get('fields', []):
                        fieldset['fields'].remove(field)

            return schema

        locals()['__patch_refs__'] = False

        self.patch_refs(
            utils, 'get_jsonschema_for_portal_type',
            get_jsonschema_for_portal_type
        )
