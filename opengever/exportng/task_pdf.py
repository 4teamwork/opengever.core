from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from opengever.base.response import IResponseContainer
from opengever.task.response_description import ResponseDescription
from plone import api
from zope.i18n import translate
import os
import requests
import logging


logger = logging.getLogger('opengever.exportng')


class TaskPDFView(BrowserView):

    template = ViewPageTemplateFile("task_pdf.pt")

    def __call__(self):

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

    def responses(self):
        transformer = api.portal.get_tool('portal_transforms')
        container = IResponseContainer(self.context)
        responses = []
        for id_, response in enumerate(container):
            description = ResponseDescription.get(response=response)
            action = translate(description.msg(), target_language='de')
            info = dict(
                id=id_,
                description=transformer.convert('html_to_text', action).getData(),
                response=response,
                action=action,
                created=response.created,
                text=response.text,
            )
            responses.append(info)
        return responses
