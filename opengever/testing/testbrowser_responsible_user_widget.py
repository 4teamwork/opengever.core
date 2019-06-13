from ftw.keywordwidget.tests.widget import AsyncKeywordWidget
from ftw.testbrowser.widgets.base import widget
from opengever.ogds.base.utils import get_current_org_unit
from Products.CMFCore.MemberDataTool import MemberData


@widget
class OpengeverResponsibleUsersAsyncKeywordWidget(AsyncKeywordWidget):
    """Autofill the correct admin unit for a responsible user."""

    @staticmethod
    def match(node):
        """Match an async keyword widget responsible(s) field.

        We optimize by using the match result of the superclass as a filter.

        As there is quite some variability to the actual field names, as per
        multi step wizards and such, we're just relying on the fact all of the
        responsible(s) fields are currently AsyncKeywordWidgets.

        Examples of field names found so far:
        ``"form.widgets.opengever-tasktemplates-tasktemplate.responsible"``
        ``"form.widgets.opengever-tasktemplates-tasktemplate-3.responsible"``
        ``"form.widgets.responsible"``
        ``"form.widgets.responsibles"``
        """
        if super(
            OpengeverResponsibleUsersAsyncKeywordWidget,
            OpengeverResponsibleUsersAsyncKeywordWidget,
        ).match(node):
            fieldname = node.node.attrib.get("data-fieldname")
            matching_suffixes = ("responsible", "responsibles")
            if fieldname and fieldname.split(".")[-1] in matching_suffixes:
                return True
        return False

    def fill(self, users, auto_org_unit=True):
        """Fill the AsyncKeywordWidget, auto.

        Mostly copied over from
        ``ftw.keywordwidget.tests.widget.AsyncKeywordWidget``.

        Can take a ``MemberData``, ``str`` or ``unicode`` object as an input.

        Having a colon in a string or a unicode input is considered a manual
        override for the org unit, or a non-user input, like a team, a foreign
        org unit or an inbox.

        Cases where a user without an admin unit is required, like search,
        are handled via ``auto_org_unit=True``.
        """
        if isinstance(users, (MemberData, str, unicode)):
            users = [users]

        if not all(isinstance(user, (MemberData, str, unicode)) for user in users):
            raise ValueError(
                "You can only pass in MemberData objects or user ID strings."
            )

        if auto_org_unit:
            org_unit = get_current_org_unit().id()
        else:
            org_unit = None

        users = tuple(self.user_to_string(user, org_unit) for user in users)
        super(OpengeverResponsibleUsersAsyncKeywordWidget, self).fill(users)

    @staticmethod
    def user_to_string(user, org_unit):
        if not isinstance(user, (str, unicode)):
            user = user.getId()
        if org_unit and ":" not in user:
            user = "{}:{}".format(org_unit, user)
        return user
