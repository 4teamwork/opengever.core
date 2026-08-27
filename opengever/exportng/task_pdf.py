from opengever.base.browser.navigation import make_tree_by_url
from opengever.base.response import IResponseContainer
from opengever.ogds.base.actor import Actor
from opengever.task.response_description import ResponseDescription
from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
import logging
import os
import requests


logger = logging.getLogger('opengever.exportng')


class TaskPDFView(BrowserView):

    template = ViewPageTemplateFile("task_pdf.pt")
    tasktree = ViewPageTemplateFile('tasktree.pt')

    def __call__(self):
        self.transformer = api.portal.get_tool('portal_transforms')
        self.subtasks = self.query_subtasks()[1:]
        data = {
            'generator': 'OneGov ExportNG'
        }
        html = self.template(self, **data)
        weasyprint_url = os.environ.get('WEASYPRINT_URL')
        try:
            resp = requests.post(weasyprint_url, files={'html': html})

            resp.raise_for_status()
        except requests.exceptions.RequestException:
            details = resp.content[:200] if resp is not None else ''
            logger.exception('PDF generation failed. %s', details)
            self.request.response.setStatus(500)
            return 'PDF generation failed.'
        else:
            self.request.response.setHeader('Content-Type', 'application/pdf')
            return resp.content

    def responses(self, task):
        container = IResponseContainer(task)
        responses = []
        for id_, response in enumerate(container):
            description = ResponseDescription.get(response=response)
            action = translate(description.msg(), target_language='de')
            info = dict(
                id=id_,
                description=self.transformer.convert('html_to_text', action).getData(),
                response=response,
                action=action,
                created=response.created,
                text=response.text,
            )
            responses.append(info)
        return responses

    def query_subtasks(self):
        catalog = api.portal.get_tool('portal_catalog')
        return catalog.unrestrictedSearchResults(
            portal_type='opengever.task.task',
            path='/'.join(self.context.getPhysicalPath()),
            sort_on='created',
        )

    def subtask_objects(self):
        return [task._unrestrictedGetObject() for task in self.subtasks]

    def create_tasktree(self):
        nodes = [
            {
                "path": item.getPath(),
                "item": item,
                "title": item.Title,
                "responsible": Actor.lookup(item.responsible).get_label(),
            }
            for item in self.subtasks
        ]
        tree = make_tree_by_url(nodes, url_key='path', children_key='children')
        return self.tasktree(children=tree, level=1)
