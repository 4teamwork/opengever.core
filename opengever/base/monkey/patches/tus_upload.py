from opengever.base.monkey.patching import MonkeyPatch


class PatchTUSUploadCleanup(MonkeyPatch):
    """Monkeypatch for plone.restapi.services.content.tus.TUSUpload

    This patches TUSUpload.cleanup() so that file system data for TUS uploads
    doesn't get cleaned up immediately during a running transaction, but
    instead is done in an afterCommmitHook, and only if the transaction was
    successful.

    This prevents the following bug that otherwise can occur:

    - A file is uploaded in the 2nd stage of a TUS upload using @tus-upload
    - The blob is added to the ZODB and file system data is cleaned up
    - But a write conflict happens when trying to commit the transaction
      - Changes to the ZODB are rolled back
      - But not the changes on the file system
      - The request is retried as part of the conflict resolution
    - On the 2nd request, the @tus-upload will not find the file system data
      for the prepared upload, and reject the upload with a 404
    """

    def __call__(self):
        import os
        import transaction

        def cleanup(self):
            """Remove temporary upload files after successful commit."""

            def cleanup_hook(commit_successful, filepath, metadata_path):
                if not commit_successful:
                    return

                if os.path.exists(filepath):
                    os.remove(filepath)
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)

            txn = transaction.get()
            txn.addAfterCommitHook(
                cleanup_hook, args=(self.filepath, self.metadata_path)
            )

        from plone.restapi.services.content.tus import TUSUpload

        self.patch_refs(TUSUpload, "cleanup", cleanup)
