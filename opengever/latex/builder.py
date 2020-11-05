from ftw.pdfgenerator.builder import Builder
from ftw.pdfgenerator.exceptions import BuildTerminated
from ftw.pdfgenerator.exceptions import PDFBuildFailed
from StringIO import StringIO
import logging
import os
import requests


logger = logging.getLogger('opengever.latex.builder')


class Builder(Builder):

    def build(self, latex):
        pdflatex_url = os.environ.get('PDFLATEX_URL')
        if pdflatex_url:
            return self.build_using_service(pdflatex_url, latex)
        else:
            return super(Builder, self).build(latex)

    def build_zip(self, latex):
        pdflatex_url = os.environ.get('PDFLATEX_URL')
        if pdflatex_url:
            return StringIO(self.build_using_service(
                pdflatex_url, latex, zip_archive=True))
        else:
            return super(Builder, self).build_zip(latex)

    def build_using_service(self, url, latex, zip_archive=False):
        if self._terminated:
            raise BuildTerminated('The build is already terminated.')

        params = {'zip': '1' if zip_archive else '0'}
        files = {'latex': ('export.tex', latex)}
        for filename in os.listdir(self.build_directory):
            key = 'file.{}'.format(filename)
            files[key] = os.path.join(self.build_directory, filename)

        resp = None
        try:
            resp = requests.post(url, params=params, files=files)
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            details = resp.content[:200] if resp is not None else ''
            logger.exception('PDF generation failed. %s', details)
            raise PDFBuildFailed()
        else:
            return resp.content


def builder_factory():
    return Builder()
