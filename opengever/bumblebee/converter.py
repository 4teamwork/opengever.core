from ftw.bumblebee.converter import BumblebeeConverter
from ftw.mail.mail import IMail


class GeverBumblebeeConverter(BumblebeeConverter):

    def _handle_store_batch(self, brains):
        """This function stores the documents and their versions in bumblebee.

        It decides if a document has to be updated  depending on its
        conversion timestamp and updates the timestamp after storing the
        document.

        Track the checksums locally by batch first and only add them to the
        global set once the transaction has been commited. Otherwise we would
        skip storing objects in case a conflict occurs.
        """
        batch_checksums = set()
        objs_to_store = []

        for brain in brains:
            obj = brain.getObject()

            if not self.needs_update(obj, self.timestamp):
                continue

            self._prepare_store_batch(obj, objs_to_store, batch_checksums)

            # don't attempt to store versions for mails, mails should not have
            # versions. in some cases they do nevertheless and then iterating
            # over versions may fail utterly. we don't like that thus we
            # avoid that it happens.
            # XXX should be fixed properly by making sure mails don't have
            # versions, ever.
            if IMail.providedBy(obj):
                continue

            for versiondata in self.prtool.getHistory(obj):
                self._prepare_store_batch(
                    versiondata.object, objs_to_store, batch_checksums)

        self._store_batch(objs_to_store)
        for obj in objs_to_store:
            self.set_conversion_timestamp(obj, self.timestamp)

        return batch_checksums
