from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import datetime
from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.inbox import _
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSourceBinder
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.base.utils import get_ou_selector
from opengever.task import _ as task_mf
from opengever.task.browser.forms import hide_feature_flagged_fields
from opengever.task.browser.forms import omit_informed_principals
from opengever.task.task import ITask
from opengever.task.task import Task
from opengever.task.util import update_reponsible_field_data
from plone.autoform import directives as form
from plone.dexterity.browser import add
from plone.dexterity.browser.edit import DefaultEditForm
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.i18n import translate
from zope.interface import implements


class IForwarding(ITask):
    """Schema interface for forwardings.
    """

    # common fieldset
    form.omitted('task_type')

    # only hide relatedItems - we need it for remembering which documents
    # should be moved after creation when creating forwarding from tabbed view.
    form.mode(relatedItems=HIDDEN_MODE)

    # additional fieldset
    form.omitted('expectedStartOfWork')
    form.omitted('expectedDuration')
    form.omitted('expectedCost')
    form.omitted('effectiveDuration')
    form.omitted('effectiveCost')

    # only hide date_of_completion, it's used
    form.mode(date_of_completion=HIDDEN_MODE)

    # make sure hidden field is not rendered in its own empty fieldset by
    # moving it to the form's first position before title
    form.order_before(date_of_completion='title')

    # deadline is not required
    deadline = schema.Date(
        title=task_mf(u"label_deadline", default=u"Deadline"),
        description=task_mf(u"help_deadline", default=u""),
        required=False,
    )

    form.widget('responsible', KeywordFieldWidget, async=True)
    responsible = schema.Choice(
        title=_(u"label_responsible", default=u"Responsible"),
        description=_(u"help_responsible", default=""),
        source=AllUsersInboxesAndTeamsSourceBinder(
            only_current_orgunit=True, include_teams=True),
        required=True,
    )


class Forwarding(Task):
    """Forwarding model class."""

    implements(IForwarding)

    @property
    def task_type_category(self):
        """Generates a Property for task categories"""
        return None

    def get_static_task_type(self):
        """Provide a marker string, which will be translated
        in the tabbedview helper method.
        """
        return 'forwarding_task_type'

    def set_static_task_type(self, value):
        """Marker set function"""
        # do not fail when trying to set the task type - but ignore
        return

    task_type = property(get_static_task_type, set_static_task_type)

    def get_task_type_label(self, language=None):
        label = _('forwarding_task_type', default=u'Forwarding')
        if language:
            return translate(
                label,
                context=self.REQUEST,
                domain='opengever.inbox',
                target_language=language,
                )

        return label


class ForwardingAddForm(add.DefaultAddForm):
    """Provide a custom add-form which adds the selected documents
    (tabbed_view) to the hidden relatedItems field and sets some defaults.
    The documents are later moved by move_documents_into_forwarding (see
    below).
    """

    portal_type = 'opengever.inbox.forwarding'

    def update(self):
        """Store default value for relatedItems in the request.

        The added objects will later be moved inside the forwarding.
        """
        paths = self.request.get('paths', [])

        search_endpoints = ('++widget++form.widgets.responsible/search',
                            '++widget++form.widgets.issuer/search',
                            '++widget++form.widgets.informed_principals/search')
        is_search_endpoint = any(
            endpoint in self.request.get('ACTUAL_URL', '') for endpoint in search_endpoints)

        if not (
                is_search_endpoint
                or paths
                or self.request.form.get('form.widgets.relatedItems', [])):
            # add status message and redirect current window back to inbox
            # but ONLY if we're not in a z3cform_inline_validation.
            IStatusMessage(self.request).addStatusMessage(
                _(
                    u'error_no_document_selected',
                    u'Error: Please select at least one document to forward.',
                    ),
                type=u'error',
                )

            redir_url = self.request.get(
                'orig_template',
                self.context.absolute_url(),
                )

            self.request.RESPONSE.redirect(redir_url)

        if paths:
            self.request.set('form.widgets.relatedItems', paths)

        # put default value for issuer into request
        if not self.request.get('form.widgets.issuer', None):
            self.request.set(
                'form.widgets.issuer',
                get_current_org_unit().inbox().id(),
                )

        # put the default responsible into the request
        if not self.request.get('form.widgets.responsible_client', None):
            org_unit = (
                get_ou_selector(ignore_anonymous=True).get_current_unit()
                )

            self.request.set('form.widgets.responsible_client', org_unit.id())

            self.request.set(
                'form.widgets.responsible',
                [org_unit.inbox().id()],
                )

        super(ForwardingAddForm, self).update()

    def updateFieldsFromSchemata(self):
        super(ForwardingAddForm, self).updateFieldsFromSchemata()
        _drop_empty_additional_fieldset(self.groups)

        hide_feature_flagged_fields(self.groups)

    def createAndAdd(self, data):
        update_reponsible_field_data(data)

        return super(ForwardingAddForm, self).createAndAdd(data=data)


class ForwardingAddView(add.DefaultAddView):
    """Define a view for adding new forwardings."""

    form = ForwardingAddForm


class ForwardingEditForm(DefaultEditForm):
    """Define a form for editing forwardings."""

    def updateFieldsFromSchemata(self):
        super(ForwardingEditForm, self).updateFieldsFromSchemata()
        _drop_empty_additional_fieldset(self.groups)

        hide_feature_flagged_fields(self.groups)
        omit_informed_principals(self.groups)

    def applyChanges(self, data):
        """Records reassign activity when the responsible has changed.

        Also update the responsible_client and responsible user.
        """
        update_reponsible_field_data(data)
        super(ForwardingEditForm, self).applyChanges(data)


def _drop_empty_additional_fieldset(groups):
    """Ensure empty 'additional' fieldset is not displayed.

    plone.autoform.base.AutoFields.updateFieldsFromSchemata initializes
    fields and groups and moves fields. However it moves fields only
    after initializing groups. Thus an empty group is left after we
    move the field (see IForwarding). The empty group renders
    a completely empty fieldset (i.e. tab in our case).

    This code performs cleanup to remove that empty group.
    """
    assert not groups[1].fields.keys(), (
        "expecting empty group, please check field definitions in "
        "IForwarding and ITask"
        )

    groups.pop(1)


def move_documents_into_forwarding(context, event):
    """When selecting documents in the tabbed view and creating a
    forwarding with this documents, they'll be added to the hidden field
    "relatedItems" (see custom AddForm above) - which is not yet the right
    place. After saving the forwarding, we need to move the documents into
    the forwarding (which did not exist before).
    We also need to clear the role assignments which are added onto related
    items upon task creation (opengever.task.localroles.set_roles_after_adding).
    """
    relations = context.relatedItems

    for relation in relations:
        obj = relation.to_object
        RoleAssignmentManager(obj).clear_by_reference(context)
        clipboard = aq_parent(aq_inner(obj)).manage_cutObjects(obj.id)
        context.manage_pasteObjects(clipboard)

    context.relatedItems = []


def set_dates(context, event):
    """Eventhandler wich set automaticly the enddate
    when a forwarding would be closed.
    """
    closing_transitions = [
        'forwarding-transition-close',
        'forwarding-transition-assign-to-dossier',
        ]

    if event.action in closing_transitions:
        context.date_of_completion = datetime.now()
