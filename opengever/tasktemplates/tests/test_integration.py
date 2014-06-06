from Products.CMFCore.utils import getToolByName
from datetime import datetime, timedelta
from ftw.builder import Builder
from ftw.builder import create
from opengever.dossier.behaviors.dossier import IDossier
from opengever.tasktemplates.interfaces import IFromTasktemplateGenerated
from opengever.testing import FunctionalTestCase
from opengever.testing import OPENGEVER_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.dexterity.utils import createContent, addContentToContainer
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent, ObjectAddedEvent


def create_testobject(parent, ptype, **kwargs):
    createContent(ptype)
    obj = createContent(ptype, **kwargs)
    notify(ObjectCreatedEvent(obj))
    obj = addContentToContainer(parent, obj, checkConstraints=False)
    notify(ObjectAddedEvent(obj))
    return obj


class TestTaskTemplates(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_TESTING

    def test_integration(self):
        """ Tests the integration of tasktemplatefolder and
        tasktemplate
        """

        portal = self.layer['portal']
        workflow = getToolByName(portal, 'portal_workflow')
        catalog = getToolByName(portal, 'portal_catalog')
        mtool = getToolByName(portal, 'portal_membership')

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        self.grant('Manager')

        # Folders and templates
        template_folder_1 = create_testobject(
            portal,
            'opengever.tasktemplates.tasktemplatefolder',
            title='TaskTemplateFolder 1')

        template_folder_2 = create_testobject(
            portal,
            'opengever.tasktemplates.tasktemplatefolder',
            title='TaskTemplateFolder 2')

        template1 = create_testobject(
            template_folder_1,
            'opengever.tasktemplates.tasktemplate',
            title='TaskTemplate 1',
            text='Test Text',
            preselected=True,
            task_type='unidirectional_by_value',
            issuer='responsible',
            responsible_client='interactive_users',
            deadline=7,
            responsible='current_user', )

        template2 = create_testobject(
            template_folder_1,
            'opengever.tasktemplates.tasktemplate',
            title='TaskTemplate 2',
            text='Test Text',
            preselected=False,
            task_type='unidirectional_by_value',
            issuer='responsible',
            responsible_client='zopemaster',
            deadline=7,
            responsible='current_user', )

        template3 = create_testobject(
            template_folder_1,
            'opengever.tasktemplates.tasktemplate',
            title='TaskTemplate 3',
            text='Test Text',
            preselected=False,
            task_type='unidirectional_by_value',
            issuer='responsible',
            responsible_client='interactive_users',
            deadline=7,
            responsible='responsible', )

        # Activate folder 1
        workflow.doActionFor(template_folder_1,
                             'tasktemplatefolder-transition-inactiv-activ')

        dossier = create_testobject(
            portal,
            'opengever.dossier.businesscasedossier',
            title='Dossier 1',
        )
        IDossier(dossier).responsible = SITE_OWNER_NAME

        add_tasktemplate_view = dossier.restrictedTraverse('add-tasktemplate')

        # We just can find folder 1 because folder 2 is inactive
        self.assertIn(
            template_folder_1.title, add_tasktemplate_view.listing(
                show='templates'))
        self.assertNotIn(
            template_folder_2.title, add_tasktemplate_view.listing(
                show='templates'))

        # Activate folder 2
        workflow.doActionFor(template_folder_2,
                             'tasktemplatefolder-transition-inactiv-activ', )

        # Now we can see both
        self.assertIn(
            template_folder_1.title, add_tasktemplate_view.listing(
                show='templates'))
        self.assertIn(
            template_folder_2.title, add_tasktemplate_view.listing(
                show='templates'))

        # In folder 1 we can find two tasktemplates
        self.assertIn(
            template1.title, add_tasktemplate_view.listing(
                show='tasks', path="/".join(
                    template_folder_1.getPhysicalPath())))

        self.assertIn(
            template2.title, add_tasktemplate_view.listing(
                show='tasks', path="/".join(
                    template_folder_1.getPhysicalPath())))

        # In folder 2 we can't find any tasktemplates
        self.assertNotIn(
            template1.title, add_tasktemplate_view.listing(
                show='tasks', path="/".join(
                    template_folder_2.getPhysicalPath())))

        self.assertNotIn(
            template2.title, add_tasktemplate_view.listing(
                show='tasks', path="/".join(
                    template_folder_2.getPhysicalPath())))

        # We create a task using the template 1
        add_tasktemplate_view.create(
            paths=["/".join(template1.getPhysicalPath())])

        # We create a task using the template 2
        add_tasktemplate_view.create(
            paths=["/".join(template2.getPhysicalPath())])

        # We create a task using the template 3
        add_tasktemplate_view.create(
            paths=["/".join(template3.getPhysicalPath())])

        # We try to create a task but we abort the transaction
        # so it won't make a new task
        add_tasktemplate_view.request['abort'] = 'yes'
        url = add_tasktemplate_view.create(
            paths=["/".join(template1.getPhysicalPath())])

        # This redirect us to the default dossier view
        self.assertEquals(url, dossier.absolute_url())

        brains = catalog(
            path='/'.join(dossier.getPhysicalPath()),
                portal_type='opengever.task.task')

        # We should have now three main Task-Objects
        # and tree subtasks objects
        self.assertEquals((3 + 3), len(brains))

        task = brains[0]
        obj = task.getObject()

        #check marker interface
        self.assertTrue(IFromTasktemplateGenerated.providedBy(obj))

        self.assertEquals(task.Title, 'TaskTemplateFolder 1')
        self.assertEquals(task.responsible, mtool.getAuthenticatedMember().getId())
        self.assertEquals(
            task.deadline,
            (datetime.today() + timedelta(template1.deadline + 5 )).date()
            )
        self.assertEquals(task.getObject().text, None)
        self.assertEquals(task.issuer, mtool.getAuthenticatedMember().getId())

        self.assertEquals(task.review_state, 'task-state-in-progress')

        # Check the subtask attributes from the template
        subtask = obj.getFolderContents()[0]

        #check marker interface
        self.assertTrue(IFromTasktemplateGenerated.providedBy(subtask.getObject()))

        self.assertEquals(subtask.Title, template1.title)
        self.assertEquals(
            subtask.responsible, mtool.getAuthenticatedMember().getId())
        self.assertEquals(
            subtask.deadline, (datetime.today() + timedelta(
                template1.deadline)).date())
        self.assertEquals(subtask.getObject().text, template1.text)
        self.assertTrue(subtask.issuer, IDossier(dossier).responsible)

        # XXX test also the event handler update_deadline
