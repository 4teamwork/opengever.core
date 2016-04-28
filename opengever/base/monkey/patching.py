from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from inspect import isclass
from inspect import isfunction
from inspect import ismethod
from inspect import ismodule
import gc
import logging


log = logging.getLogger('opengever.base.monkey')

VERBOSE = False


class MonkeyPatch(object):
    """Base class for all monkey patches.

    This class provides helper methods that offer different strategies for
    monkey patching and unify logging of what's being patched.
    """

    def patch_refs(self, scope, original_name, replacement):
        """Monkey patch a method or function and all references to it.
        """
        original = getattr(scope, original_name)
        if not (isfunction(original) or ismethod(original)):
            raise Exception(
                "Refusing to patch references to anything other than "
                "functions or methods! You most likely DONT want to update "
                "all references to primitive values like ints or strings!")

        scope_name = self._get_scope_name(scope)
        log.info("Patching %s.%s" % (scope_name, original_name))

        # replace the initial reference by using setattr:
        # some classes have a `dictproxy` as their __dict__, which is immutable
        # and doesn't seem to support garbage collection - so its references
        # won't be found by gc.get_referrers().
        setattr(scope, original_name, replacement)

        # replace any other references
        self._global_replace(original, replacement)

    def _global_replace(self, original, replacement):
        """Replace all references to object 'original' with object
        'replacement' in all dictionaries (i.e. module and class scopes for
        functions / methods).

        Based on Labix mocker's global_replace().
        """
        for referrer in gc.get_referrers(original):
            if type(referrer) is not dict:
                if VERBOSE:
                    log.info("  Skipping referrer %r" % referrer)
                continue

            if referrer.get("__patch_refs__", True):
                scope_name = referrer.get('__name__', '<unknown scope>')
                for key, value in list(referrer.iteritems()):
                    if value is original:
                        log.info("  Replacing reference %r in %s" % (
                            key, scope_name))
                        referrer[key] = replacement

    def patch_class_security(self, klass, method_name, new_permission):
        """Monkey patch class security definitions to protect a method with
        a different permission.
        """
        def reset_security_for_attribute(name, klass):
            """Remove security declarations for a particular method /
            attribute by filtering declarations for that attribute from
            __ac_permissions__.
            """
            new_ac_permissions = []

            for permission_mapping in klass.__ac_permissions__:
                permission, names = permission_mapping
                if name not in names:
                    new_ac_permissions.append(permission_mapping)
                else:
                    new_names = tuple([n for n in names if n != name])
                    modified_mapping = (permission, new_names)
                    new_ac_permissions.append(modified_mapping)

            klass.__ac_permissions__ = tuple(new_ac_permissions)

        reset_security_for_attribute(method_name, klass)
        sec = ClassSecurityInfo()
        sec.declareProtected(new_permission, method_name)
        sec.apply(klass)
        InitializeClass(klass)

    def patch_value(self, scope, original_name, replacement):
        """Monkey patch a single value.
        """
        scope_name = self._get_scope_name(scope)
        log.info("Patching %s.%s to %r" % (
            scope_name, original_name, replacement))
        setattr(scope, original_name, replacement)

    def _get_scope_name(self, scope):
        if isclass(scope):
            mod_name = scope.__module__
            scope_name = '.'.join((mod_name, scope.__name__))
        elif ismodule(scope):
            scope_name = scope.__name__
        else:
            scope_name = '<unknown scope>'
        return scope_name
