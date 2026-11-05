from ftw.testbrowser import TRAVERSAL_BROWSER_FIXTURE
from opengever.core.docker_testing import DockerServiceLayer
from opengever.core.testing import ContentFixtureLayer
from opengever.core.testing import GEVERIntegrationTesting
import os
import psycopg2


class ExportNGDBLayer(DockerServiceLayer):
    port_env = 'PORT10'
    image_name = 'postgres:18-alpine'
    service_url_env = 'EXPORTNG_DSN'

    def start_container(self):
        self.run(
            'docker run --pull always -d -p {}:5432 --name {}'
            ' -e POSTGRES_DB=exportng -e POSTGRES_USER=exportng -e POSTGRES_PASSWORD=secret'
            ' --mount type=tmpfs,dst=/var/lib/postgresql,tmpfs-size=100000000 {}'
            ' postgres --fsync=off --synchronous-commit=off --full-page-writes=off'.format(
                self.port, self.container_name, self.image_name))
        os.environ[self.service_url_env] = 'postgresql://exportng:secret@127.0.0.1:{}/exportng'.format(self.port)

    def healthcheck(self):
        try:
            psycopg2.connect(
                dbname='exportng',
                user='exportng',
                password='secret',
                host='127.0.0.1',
                port=self.port,
            )
        except psycopg2.errors.OperationalError:
            return False
        else:
            return True


EXPORTNG_DB_FIXTURE = ExportNGDBLayer()
EXPORTNG_DB_INTEGRATION_TESTING = GEVERIntegrationTesting(
    bases=(ContentFixtureLayer(), TRAVERSAL_BROWSER_FIXTURE, EXPORTNG_DB_FIXTURE),
    name="opengever.core:exportng-db-integration")
