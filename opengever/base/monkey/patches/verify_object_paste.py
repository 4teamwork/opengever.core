from opengever.base.monkey.patching import MonkeyPatch


class PatchCopyContainerVerifyObjectPaste(MonkeyPatch):
    """Patch `OFS.CopySupport.CopyContainer._verifyObjectPaste`
    to disable `Delete objects` permission check when moving items.
    """

    def __call__(self):
        from AccessControl import getSecurityManager
        from AccessControl import Unauthorized
        from Acquisition import aq_inner
        from Acquisition import aq_parent
        from App.Dialogs import MessageDialog
        from cgi import escape
        from OFS.CopySupport import absattr
        from OFS.CopySupport import CopyError
        from opengever.document.behaviors import IBaseDocument
        from ZODB.POSException import ConflictError

        def _verifyObjectPaste(self, object, validate_src=1):
            # Verify whether the current user is allowed to paste the
            # passed object into self. This is determined by checking
            # to see if the user could create a new object of the same
            # meta_type of the object passed in and checking that the
            # user actually is allowed to access the passed in object
            # in its existing context.
            #
            # Passing a false value for the validate_src argument will skip
            # checking the passed in object in its existing context. This is
            # mainly useful for situations where the passed in object has no
            # existing context, such as checking an object during an import
            # (the object will not yet have been connected to the acquisition
            # heirarchy).
            #
            # We also make sure that we are not pasting a checked-out document

            if IBaseDocument.providedBy(object) and object.is_checked_out():
                raise CopyError('Checked out documents cannot be copied.')

            if not hasattr(object, 'meta_type'):
                raise CopyError(MessageDialog(
                      title   = 'Not Supported',
                      message = ('The object <em>%s</em> does not support this' \
                                 ' operation' % escape(absattr(object.id))),
                      action  = 'manage_main'))

            if not hasattr(self, 'all_meta_types'):
                raise CopyError(MessageDialog(
                      title   = 'Not Supported',
                      message = 'Cannot paste into this object.',
                      action  = 'manage_main'))

            mt_permission = None
            meta_types = absattr(self.all_meta_types)

            for d in meta_types:
                if d['name'] == object.meta_type:
                    mt_permission = d.get('permission')
                    break

            if mt_permission is not None:
                sm = getSecurityManager()

                if sm.checkPermission(mt_permission, self):
                    if validate_src:
                        # Ensure the user is allowed to access the object on the
                        # clipboard.
                        try:
                            parent = aq_parent(aq_inner(object))
                        except ConflictError:
                            raise
                        except Exception:
                            parent = None

                        if not sm.validate(None, parent, None, object):
                            raise Unauthorized(absattr(object.id))

                        # --- Patch ---
                        # Disable checking for `Delete objects` permission

                        # if validate_src == 2: # moving
                        #     if not sm.checkPermission(delete_objects, parent):
                        #         raise Unauthorized('Delete not allowed.')

                        # --- End Patch ---
                else:
                    raise CopyError(MessageDialog(
                        title = 'Insufficient Privileges',
                        message = ('You do not possess the %s permission in the '
                                   'context of the container into which you are '
                                   'pasting, thus you are not able to perform '
                                   'this operation.' % mt_permission),
                        action = 'manage_main'))
            else:
                raise CopyError(MessageDialog(
                    title = 'Not Supported',
                    message = ('The object <em>%s</em> does not support this '
                               'operation.' % escape(absattr(object.id))),
                    action = 'manage_main'))

        from OFS.CopySupport import CopyContainer
        self.patch_refs(CopyContainer, '_verifyObjectPaste', _verifyObjectPaste)
