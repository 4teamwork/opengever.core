from ftw.upgrade import UpgradeStep
from opengever.base.response import IResponseContainer
from opengever.base.response import Response
from opengever.task.adapters import IResponseContainer as OldIResponseContainer
from opengever.task.task import ITask
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations


class MigrateOldTaskResponsesToNewResponsesImplementation(UpgradeStep):
    """Migrate old task responses to new responses implementation.
    """

    def __call__(self):
        self.install_upgrade_profile()
        for task in self.objects({'object_provides': ITask.__identifier__},
                                 'Migrate task responses to new responses implementation'):
            self.migrate_responses(task)

    def migrate_responses(self, task):
        container = IResponseContainer(task)
        old_container = OldIResponseContainer(task)
        for old_response in old_container:
            response = Response()

            if old_response.text:
                response.text = old_response.text

            if old_response.rendered_text:
                response.rendered_text = old_response.rendered_text

            if old_response.transition:
                response.transition = old_response.transition

            if old_response.changes:
                for change in old_response.changes:
                    response.add_change(
                        change.get('id'),
                        change.get('before'),
                        change.get('after'),
                        change.get('name'))

            if old_response.creator:
                response.creator = old_response.creator

            if old_response.date:
                response.created = old_response.date.asdatetime().replace(tzinfo=None)

            if old_response.type:
                response.response_type = old_response.type

            if old_response.type:
                response.mimetype = old_response.mimetype

            if old_response.relatedItems:
                response.related_items = PersistentList(old_response.relatedItems)

            if old_response.added_object:
                added_objects = old_response.added_object
                if not hasattr(added_objects, '__iter__'):
                    added_objects = [added_objects]

                response.added_objects = PersistentList(added_objects)

            if old_response.successor_oguid:
                response.successor_oguid = old_response.successor_oguid

            container.add(response)

        annotations = IAnnotations(task)
        if old_container.ANNO_KEY in annotations:
            # We do not delete the old responses but backup it in a different
            # annotations-key. As soon as we completely remove the old implementation
            # we can remove the backup. Otherwise we won't have the possibilty to
            # restore any response if there went soemthing wrong.
            # Just leaving the responses under the same key is not an option.
            # Running the upgradestep twice would duplicate the migrated responses.
            annotations['backup-{}'.format(old_container.ANNO_KEY)] = annotations[old_container.ANNO_KEY]
            del annotations[old_container.ANNO_KEY]
