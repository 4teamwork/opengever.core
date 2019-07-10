from opengever.core.cached_testing import BUILDOUT_DIR
from threading import Thread
import atexit
import io
import os
import requests
import signal
import socket
import subprocess
import time


class SolrServer(object):
    """The SolrServer singleton is in charge of starting and stopping the solr server.
    """

    @classmethod
    def get_instance(klass):
        if not hasattr(klass, '_instance'):
            klass._instance = klass()
        return klass._instance

    def configure(self, port, core):
        self._configured = True
        self.port = int(port)
        self.core = core
        SolrReplicationAPIClient.get_instance().configure(port, core)
        return self

    def start(self):
        """Start the solr server in a subprocess.
        """
        assert not self._running, 'Solr was already started.'
        self._require_configured()
        self._thread = Thread(target=self._run_server_process)
        self._thread.daemon = True
        self._thread.start()
        atexit.register(self.stop)
        self._running = True
        return self

    def stop(self):
        """Make sure the solr server is stopped.
        """
        if not self._running:
            return self

        self._require_configured()
        try:
            os.kill(self._process.pid, signal.SIGINT)
        except KeyboardInterrupt:
            pass
        except OSError as exc:
            if exc.strerror != 'No such process':
                raise
        self._thread.join()
        self._running = False
        return self

    def is_ready(self):
        """Check whether the solr server has bound the port already.
        """
        sock = socket.socket()
        sock.settimeout(0.1)
        try:
            result = sock.connect_ex(('127.0.0.1', self.port))
        finally:
            sock.close()
        return result == 0

    def await_ready(self, timeout=60, interval=0.1, verbose=False):
        """Wait until the solr server has bound the port.
        """
        self._require_configured()
        for index in range(int(timeout / interval)):
            if self.is_ready():
                return self
            if verbose:
                print '... waiting for solr ({})'.format(index)
            time.sleep(interval)

        self.print_tail()
        raise ValueError('Timeout ({}s) while waiting for solr.'.format(timeout))

    def print_tail(self, max_lines=100):
        """Print the last lines of the captured stdout of the solr server.
        """
        print '\n'.join(self._stdout.getvalue().split('\n')[-max_lines:])

    def __init__(self):
        assert not hasattr(type(self), '_instance'), 'Use SolrServer.get_instance()'
        self._configured = False
        self._running = False

    def _run_server_process(self):
        command = ['bin/solr', 'fg']
        env = os.environ.copy()
        env.setdefault('SOLR_PORT', str(self.port))
        self._stdout = io.StringIO()
        self._process = subprocess.Popen(command, stdout=subprocess.PIPE, env=env)
        while True:
            if self._process.poll():
                return
            self._stdout.writelines((self._process.stdout.readline().decode('utf-8'),))

    def _require_configured(self):
        if not self._configured:
            raise ValueError('Configure first with SolrServer.get_instance().configure()')


class SolrReplicationAPIClient(object):
    """This is a client for the Solr Replication API.

    See https://lucene.apache.org/solr/guide/7_6/making-and-restoring-backups.html
    for details regarding the Replication API.

    Basic usage:

    - Start Solr on SOLR_PORT
    - If necessary, delete all data in Solr. For example using
      curl http://localhost:12333/solr/solrtest/update?commit=true -H "Content-type: application/json" --data-binary "{'delete': {'query': '*:*'}}"
    - Pick a unique backup name below. Backups will be created in
      var/solr/solrtest/data/
    - Run the tests below
    """

    @classmethod
    def get_instance(klass):
        if not hasattr(klass, '_instance'):
            klass._instance = klass()
        return klass._instance

    def configure(self, port, core):
        self._configured = True
        self.port = int(port)
        self.core = core
        self.base_url = 'http://localhost:{}/solr/{}'.format(port, core)
        return self

    def __init__(self):
        assert not hasattr(type(self), '_instance'), 'Use SolrReplicationAPIClient.get_instance()'
        self._configured = False
        self.session = requests.session()
        self.session.headers.update({'Accept': 'application/json'})

    def clear(self):
        """Delete all documents from Solr.
        """
        self._require_configured()
        response = requests.get(self.base_url + '/update?commit=true',
                                json={'delete': {'query': '*:*'}})
        try:
            response.raise_for_status()
        except Exception:
            print response.json()
            raise
        return response.json()

    def create_backup(self, name):
        """Create a backup of the snapshot state identified by `name`.
        """
        self._require_configured()
        backup_name = 'bak-{}'.format(name)

        # When the backup exists, delete it. Solr can't do that.
        backup_path = BUILDOUT_DIR.joinpath(
            'var', 'solr', self.core, 'data', 'snapshot.{}'.format(backup_name))
        if backup_path.exists():
            backup_path.rmtree()

        # First, trigger solr commit so that changes are writte to disk.
        self.session.get(url=self.base_url + '/update?commit=true').raise_for_status()

        response = self.session.get(url=self.base_url + '/replication',
                                    params={'command': 'backup', 'name': backup_name})
        try:
            response.raise_for_status()
        except Exception:
            print response.json()
            raise
        return response

    def restore_backup(self, name):
        """Restore a backup. `name` refers to the snapshot name.
        """
        self._require_configured()
        response = self.session.get(url=self.base_url + '/replication',
                                    params={'command': 'restore', 'name': 'bak-{}'.format(name)})
        try:
            response.raise_for_status()
        except Exception:
            print response.json()
            raise
        return response

    def restore_status(self):
        """Check for the progress of a running restore operation.
        """
        self._require_configured()
        response = self.session.get(url=self.base_url + '/replication',
                                    params={'command': 'restorestatus'})
        try:
            response.raise_for_status()
        except Exception:
            print response.json()
            raise
        response_data = response.json()

        # Only newer Solr versions have a response (!) status
        if 'status' in response_data and response_data['status'] != 'OK':
            print response
            print response_data
            raise Exception('Failed to check restore status')

        return response_data['restorestatus']

    def await_restored(self, timeout=60, interval=0.1):
        """Block until the solr server has no restore in progress.
        """
        for index in range(int(timeout / interval)):
            status = self.restore_status()
            if status['status'] == 'No restore actions in progress':
                return
            if status['status'] not in ('success', 'In Progress'):
                raise ValueError('Unexpected restore status: {!r}'.format(status['status']))
            if status['status'] == 'success':
                return
            time.sleep(interval)

        raise ValueError('Timeout ({}s) while waiting for restore to finish.'.format(timeout))

    def _require_configured(self):
        if not self._configured:
            raise ValueError('Configure first with SolrServer.get_instance().configure()')


if __name__ == '__main__':
    # selftest:
    # ./bin/zopepy opengever/core/solr_testing.py
    port = 18988
    core = 'fritz'
    SolrReplicationAPIClient.get_instance().configure(port, core)
    server = SolrServer.get_instance().configure(port)

    server.start()
    print '... starting'
    server.await_ready(verbose=True)
    print '... solr output:'
    server.print_tail(max_lines=10)
    print '... stopping'
    server.stop()
    print '... finished'
