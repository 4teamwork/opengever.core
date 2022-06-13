from DateTime import DateTime
from ftw.upgrade import UpgradeStep
from plone import api
from Products.CMFCore.WorkflowCore import WorkflowException


class FixMailReviewHistory(UpgradeStep):
    """Fix mail review_history.
    """

    deferrable = True

    def __call__(self):
        wftool = api.portal.get_tool('portal_workflow')

        # The problem has been fixed on 20 Now 2014 with the commit
        # 3cf26ce1edf9bb665d0df6719d95b9aad32d3d53, so we calculate two
        # additional years to make sure the change has been installed in
        # production
        query = {'portal_type': 'ftw.mail.mail',
                 'created': {'query': DateTime(2016, 11, 20), 'range': 'max'}}

        for mail in self.objects(query, 'Fix mail review_history'):
            try:
                wftool.getInfoFor(mail, "review_history")
            except WorkflowException:
                continue

            self.fix_workflow_history(mail)

    def fix_workflow_history(self, mail):
        wf_history = mail.workflow_history
        if not wf_history:
            return

        if 'opengever_mail_workflow' not in wf_history:
            return

        new_history = []
        for entry in wf_history.get('opengever_mail_workflow'):
            if 'state' in entry.keys():
                entry['review_state'] = entry.pop('state')

            new_history.append(entry)

        wf_history['opengever_mail_workflow'] = tuple(new_history)
