from opengever.base.monkey.patching import MonkeyPatch
from opengever.base.sentry import log_msg_to_sentry
from opengever.debug.stacktrace import save_stacktrace
from opengever.debug.write_on_read_tracing import format_instruction
from plone import api
from plone.dexterity.interfaces import IDexterityContent
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IUUIDAware
from ZODB.POSException import ConflictError
import logging
import transaction


log = logging.getLogger('opengever.debug')


def check_modified_in_sync(succeeded, obj, instruction):
    """Post-commit hook to check that modified is in sync after commit."""
    if not succeeded:
        return

    # the object is not aq-wrapped so we query by its UID
    obj_uid = IUUID(obj)
    query = {'UID': obj_uid}
    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog.unrestrictedSearchResults(query)
    if len(brains) != 1:
        log.warn(u'Error when querying for: {} {}'.format(
            repr(obj), query)
        )
        return

    brain = brains[0]
    if brain.modified == obj.modified():
        # all is well if modified is equal
        return

    # we have an object where object modification date is out
    # of sync with the modification date in catalog, we log it
    # and report the issue to sentry, also providing the
    # already serialized traceback
    msg = u'Out of sync modified detected.'
    formatted_traceback = format_instruction(instruction)

    log.warning(msg)
    log.warning(formatted_traceback)
    log.warning(u'object: {}, uid: {}'.format(
        repr(obj), obj_uid))

    log_msg_to_sentry(
        msg, context=obj, level='warning',
        string_max_length=len(formatted_traceback),
        extra={
            'stacktrace': formatted_traceback,
            'object_out_of_sync': repr(obj),
            'object_out_of_sync_uid': obj_uid,
        }
    )


class PatchConnectionRegister(MonkeyPatch):
    """Patched version of ZODB.Connection.Connection.register to track
    when modified becomes out of sync after an object has been changed.

    Will register an after-commit hook for each dexterity content
    object thas is changed/added. The hook will verify that modified is
    in sync with the catalog and log to sentry if it detects an out of
    sync state.

    CAUTION: This will be called for every change to a persistent object,
    be very careful here!
    """
    def __call__(self):
        def register_patched_to_check_modified(self, obj):
            orig_register_func(self, obj)

            # only perform checks for dexterity content objects, skip
            # everything else
            if not IDexterityContent.providedBy(obj):
                return

            # we will get the object's IUUID in the post-commit hook, prevent
            # registering it and saving the trace for objects that don't
            # support IUUID for some reason
            if not IUUIDAware.providedBy(obj):
                return

            try:
                instruction = save_stacktrace(obj)
                # we add a post-commit hook for just this object, each
                # registered content object will have its own hook with its
                # own traceback
                transaction.get().addAfterCommitHook(
                    check_modified_in_sync, args=[obj, instruction])
            except ConflictError:
                raise
            except Exception, e:
                log.warn('Error when trying to save stacktrace: {}'.format(
                    str(e)))

        from ZODB.Connection import Connection
        locals()['__patch_refs__'] = False
        orig_register_func = Connection.register
        self.patch_refs(Connection, 'register', register_patched_to_check_modified)
