from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_filters
from opengever.activity.model.watcher import Watcher
from opengever.base.model import create_session
from opengever.base.sentry import log_msg_to_sentry
from opengever.base.solr import OGSolrDocument
from opengever.base.txnutils import registered_objects
from opengever.base.txnutils import txn_is_dirty
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.inbox.forwarding import IForwarding
from opengever.ogds.models.user import User
from opengever.task.activities import TaskChangeIssuerActivity
from opengever.task.response_syncer import sync_task_response
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getUtility
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectModifiedEvent
import logging
import transaction


logger = logging.getLogger('opengever.api')


class ExtractOldNewUserMixin(Service):
    """This mixin privdes a method to extract and validate the old and the new
    userid from the request body.
    """
    def extract_userids(self):
        data = json_body(self.request)
        old_userid = data.get("old_userid")
        new_userid = data.get("new_userid")

        # In case of a context action, we receive a dict for the old_userid,
        # from which we need to extract the token.

        # example:
        # 'old_userid': {u'token': u'ben.utzer', u'title': u'Utzer Ben (ben.utzer)'}
        if isinstance(old_userid, dict):
            old_userid = old_userid.get('token')

        if not old_userid:
            raise BadRequest("Property 'old_userid' is required")
        if not new_userid:
            raise BadRequest("Property 'new_userid' is required")
        if not User.query.get_by_userid(old_userid):
            raise BadRequest("userid '{}' does not exist".format(old_userid))
        if not User.query.get_by_userid(new_userid):
            raise BadRequest("userid '{}' does not exist".format(new_userid))
        if old_userid == new_userid:
            raise BadRequest("'old_userid' and 'new_userid' should not be the same")

        return old_userid, new_userid


class TransferTaskPost(ExtractOldNewUserMixin, Service):

    def reply(self):
        self.old_userid, self.new_userid = self.extract_userids()

        # Create watcher for new issuer/responsible if it doesn't exist yet
        # and commit, in order to avoid a deadlock when both sides of an
        # inter-admin-unit would attempt to do this. See GEVER-946.
        self.create_watcher_and_commit_if_needed(self.new_userid)

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        self.request.environ['HTTP_X_GEVER_SUPPRESSNOTIFICATIONS'] = 'True'

        if IForwarding.providedBy(self.context):
            responsible_transition = 'forwarding-transition-reassign'
            issuer_transition = 'forwarding-transition-change-issuer'
        else:
            responsible_transition = 'task-transition-reassign'
            issuer_transition = 'task-transition-change-issuer'

        # Clear any potential reminders for the old user
        self.context.clear_reminder(self.old_userid)

        issuer_change = self.old_userid == self.context.issuer
        responsible_change = self.old_userid == self.context.responsible

        if issuer_change:
            self.change_issuer(
                transition=issuer_transition,
                new_issuer=self.new_userid)

        if responsible_change:
            self.change_responsible(
                transition=responsible_transition,
                new_responsible=self.new_userid)

        self.request.response.setStatus(204)
        return super(TransferTaskPost, self).reply()

    def change_responsible(self, transition, new_responsible):
        """Change the responsible by reusing the "reassign task" mechanism.

        This will trigger the *-transition-reassign WF transition, and all
        necessary changes plus syncing to potential predecessors / succeessors
        will be done in the respective ITransitionExtender.
        """
        wftool = api.portal.get_tool('portal_workflow')

        # It's implied that the responsible OrgUnit should never change
        # when transferring a task.
        old_responsible_client = self.context.responsible_client
        params = {
            'responsible': new_responsible,
            'responsible_client': old_responsible_client
        }
        wftool.doActionFor(self.context, transition, transition_params=params)

    def change_issuer(self, transition, new_issuer):
        """Change the issuer by emulating some of the 'reassign' behavior.

        The main difference is that we don't have a real workflow transition
        that we need to invoke for an issuer change - instead we use a
        pseudo-transition that is just a translated string that is used to
        make it look like a state change in the task's response timeline.
        """
        changes = [(ITask['issuer'], new_issuer)]

        issuer_response = add_simple_response(
            self.context, transition=transition,
            field_changes=changes,
            supress_events=True)

        self.context.issuer = new_issuer
        notify(ObjectModifiedEvent(self.context))
        TaskChangeIssuerActivity(self.context, self.context.REQUEST, issuer_response).record()

        sync_task_response(
            self.context, self.request, 'issuer-change',
            transition, text=None, new_issuer=new_issuer)

    def create_watcher_and_commit_if_needed(self, new_responsible):
        """If we don't have an entry in the 'watchers' table for the
        new responsible, that would lead to a deadlock when reassigning an
        inter-admin-unit task, because both sides would attempt to create
        it (with the second txn not seeing the pending changes of the
        first one, because of isolation).

        We therefore create it here to be sure, and immediately commit, making
        sure the txn is in a clean that so we don't commit any unexpected
        changes by accident (otherwise we log to Sentry).
        """
        watcher = Watcher.query.get_by_actorid(new_responsible)
        if not watcher:

            if txn_is_dirty():
                # Creating and committing the watcher should always be the
                # first thing that's being done in the txn when reassigning.
                # Otherwise we would be committing unrelated, unexpected
                # changes.
                #
                # Detect if that happens, but still proceed and log to sentry.
                msg = 'Dirty transaction when creating and committing watcher'
                logger.warn(msg)
                logger.warn('Registered objects: %r' % registered_objects())
                log_msg_to_sentry(msg, level='warning', extra={
                    'registered_objects': repr(registered_objects())}
                )

            session = create_session()
            watcher = Watcher(actorid=new_responsible)
            session.add(watcher)
            transaction.commit()
            transaction.begin()


class TransferDossierPost(ExtractOldNewUserMixin, Service):
    """Transfers a dossier and optionally all of its subdossiers from one
    responsible to another.
    """

    def reply(self):
        old_userid, new_userid = self.extract_userids()
        recursive = json_body(self.request).get('recursive', True)

        if not self.context.is_open():
            raise BadRequest("Only open dossiers can be transfered to another user")

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        self.request.environ['HTTP_X_GEVER_SUPPRESSNOTIFICATIONS'] = 'True'

        self.transfer_dossier(self.context, old_userid, new_userid, recursive)

        self.request.response.setStatus(204)
        return super(TransferDossierPost, self).reply()

    def transfer_dossier(self, dossier, old_userid, new_userid, recursive=True):
        if recursive:
            solr = getUtility(ISolrSearch)
            query = {'path': {'query': '/'.join(self.context.getPhysicalPath()),
                              'depth': -1},
                     'object_provides': IDossierMarker.__identifier__,
                     'responsible': old_userid,
                     'review_state': DOSSIER_STATES_OPEN}
            dossiers_to_transfer = [OGSolrDocument(doc).getObject() for doc in
                                    solr.search(filters=make_filters(**query), fl=["path"]).docs]
        else:
            dossiers_to_transfer = [self.context]

        for dossier in dossiers_to_transfer:
            IDossier(dossier).responsible = new_userid

            # We have to trigger an object modified event to get a jorunal entry
            # and reindex the object.
            notify(ObjectModifiedEvent(dossier))
