from opengever.redis.client import redis_client_manager
from plone.testing import Layer
import os
import redis
import requests
import shlex
import socket
import subprocess
import time


class DockerServiceLayer(Layer):
    """A base class for layers that starts a Docker container on setup and
       stops it on teardown.
       Subclass this layer for specific services.
    """

    port_env = None
    image_name = None
    service_url_env = None

    def setUp(self):
        self.port = os.environ.get(self.port_env, self.find_free_port())
        base_name = self.image_name.split(':')[0].replace('/', '_')
        self.container_name = '{}_{}'.format(base_name, self.port)
        self.start_container()
        self.wait_until_ready()

    def tearDown(self):
        self.run('docker stop {}'.format(self.container_name))
        self.run('docker rm {}'.format(self.container_name))
        del os.environ[self.service_url_env]

    def start_container(self):
        self.run(
            'docker run --pull always -d -p {}:8080 --name {} {}'.format(
                self.port, self.container_name, self.image_name))
        os.environ[self.service_url_env] = 'http://localhost:{}/'.format(self.port)

    def healthcheck(self):
        try:
            requests.get('http://localhost:{}/healthcheck'.format(self.port))
        except requests.ConnectionError:
            return False
        else:
            return True

    def wait_until_ready(self, timeout=10):
        start = now = time.time()
        while now - start < timeout:
            if self.healthcheck():
                return True
            time.sleep(0.1)
            now = time.time()

        return False

    def run(self, cmd):
        args = shlex.split(cmd)
        proc = subprocess.Popen(
            args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = proc.communicate()
        if proc.returncode != 0:
            assert False, "Running '{}' failed. Command returned: {}".format(cmd, err)

    def find_free_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        return port


class MSGConvertServiceLayer(DockerServiceLayer):
    port_env = 'PORT5'
    image_name = '4teamwork/msgconvert:latest'
    service_url_env = 'MSGCONVERT_URL'


class PDFLatexServiceLayer(DockerServiceLayer):
    port_env = 'PORT6'
    image_name = '4teamwork/pdflatex:latest'
    service_url_env = 'PDFLATEX_URL'


class SablonServiceLayer(DockerServiceLayer):
    port_env = 'PORT7'
    image_name = '4teamwork/sablon:latest'
    service_url_env = 'SABLON_URL'


class WeasyPrintServiceLayer(DockerServiceLayer):
    port_env = 'PORT8'
    image_name = '4teamwork/weasyprint:latest'
    service_url_env = 'WEASYPRINT_URL'


class RedisServiceLayer(DockerServiceLayer):
    port_env = 'PORT9'
    image_name = 'redis:6.2-alpine'
    service_url_env = 'REDIS_URL'

    def testSetUp(self):
        super(RedisServiceLayer, self).testSetUp()
        redis_client_manager.get_client().flushdb()

    def start_container(self):
        self.run(
            'docker run --pull always -d -p {}:6379 --name {} {}'.format(
                self.port, self.container_name, self.image_name))
        os.environ[self.service_url_env] = 'redis://localhost:{}/'.format(self.port)

    def healthcheck(self):
        try:
            redis_client_manager.get_client().ping()
        except redis.ConnectionError:
            return False
        else:
            return True


MSGCONVERT_SERVICE_FIXTURE = MSGConvertServiceLayer()
PDFLATEX_SERVICE_FIXTURE = PDFLatexServiceLayer()
SABLON_SERVICE_FIXTURE = SablonServiceLayer()
WEASYPRINT_SERVICE_FIXTURE = WeasyPrintServiceLayer()
REDIS_SERVICE_FIXTURE = RedisServiceLayer()
