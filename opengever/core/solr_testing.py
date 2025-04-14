from collective.indexing.queue import processQueue
from ftw.solr.interfaces import ISolrConnectionManager
from path import Path
from requests.exceptions import ConnectionError
from zope.component import getUtility
import atexit
import os
import requests
import subprocess
import time


BUILDOUT_DIR = Path(os.environ.get('BUILDOUT_DIR', Path(__file__).joinpath('..', '..', '..').abspath()))


class SolrServer(object):
    """The SolrServer singleton is in charge of starting and stopping the solr server.
    """

    @classmethod
    def get_instance(klass):
        if not hasattr(klass, '_instance'):
            klass._instance = klass()
        return klass._instance

    def configure(self, port, core, hostname='localhost'):
        self._configured = True
        self.hostname = hostname
        self.port = int(port)
        self.core = core
        self.container_name = 'opengever_testserver_solr_{}'.format(self.port)
        SolrReplicationAPIClient.get_instance().configure(
            port, core, hostname, container_name=self.container_name)
        return self

    def start(self):
        """Start the solr server in a subprocess.
        """
        assert not self._running, 'Solr was already started.'
        self._require_configured()

        command = [
            'docker',
            'run',
            '--pull',
            'always',
            '-d',
            '--rm',
            '-p',
            '{}:8983'.format(self.port),
            '-e',
            'SOLR_CORES=testing functionaltesting testserver',
            '--name',
            self.container_name,
            '4teamwork/ogsolr:9.8.1',
            'solr-foreground',
        ]

        proc = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = proc.communicate()
        if proc.returncode != 0:
            assert False, "Running Solr with Docker failed. Command returned: {}".format(err)

        atexit.register(self.stop)
        self._running = True
        return self

    @property
    def connection(self):
        """Provide access to the currently active solr connection.
        """
        manager = getUtility(ISolrConnectionManager)

        if not self._configured or manager.connection is None:
            raise Exception("Attempt to commit Solr in a test that didn't set "
                            "up Solr (properly). Make sure your test case uses "
                            "the OPENGEVER_SOLR_INTEGRATION_TESTING layer.")

        processQueue()
        return manager.connection

    def commit(self, after_commit=False):
        """Commit any pending updates in Solr.
        """
        self.connection.commit(after_commit=after_commit)

    def stop(self):
        """Make sure the solr server is stopped.
        """
        if not self._running:
            return self

        self._require_configured()

        command = ['docker', 'stop', self.container_name]
        proc = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = proc.communicate()
        if proc.returncode != 0:
            assert False, "Stopping of Solr container failed. Command returned: {}".format(err)

        self._running = False
        return self

    def is_ready(self):
        """Check whether the solr server is ready to accept connections.
        """
        url = 'http://{}:{}/solr/{}/admin/ping'.format(
            self.hostname, self.port, self.core)
        response = requests.get(url=url)
        return response.ok

    def await_ready(self, timeout=60, interval=0.1, verbose=False):
        """Wait until the solr server has bound the port.
        """
        self._require_configured()
        for index in range(int(timeout / interval)):
            try:
                ready = self.is_ready()
            except ConnectionError:
                ready = False
            if ready:
                return self
            if verbose:
                print '... waiting for solr ({})'.format(index)
            time.sleep(interval)

        raise ValueError('Timeout ({}s) while waiting for solr.'.format(timeout))

    def print_tail(self, max_lines=100):
        """Print the last lines of the captured stdout of the solr server.
        """
        print '\n'.join(self._stdout.getvalue().split('\n')[-max_lines:])

    def __init__(self):
        assert not hasattr(type(self), '_instance'), 'Use SolrServer.get_instance()'
        self._configured = False
        self._running = False

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
      curl http://localhost:12333/solr/solrtest/update?commit=true -H "Content-type: application/json" --data-binary "{'delete': {'query': '*:*'}}"  # noqa
    - Pick a unique backup name below. Backups will be created in
      var/solr/solrtest/data/
    - Run the tests below
    """

    @classmethod
    def get_instance(klass):
        if not hasattr(klass, '_instance'):
            klass._instance = klass()
        return klass._instance

    def configure(self, port, core, hostname='localhost', container_name=None):
        self._configured = True
        self.hostname = hostname
        self.port = int(port)
        self.core = core
        self.container_name = container_name
        self.base_url = 'http://{}:{}/solr/{}'.format(self.hostname, port, core)
        return self

    def __init__(self):
        assert not hasattr(type(self), '_instance'), 'Use SolrReplicationAPIClient.get_instance()'
        self._configured = False
        self.session = requests.session()
        self.session.headers.update({'Accept': 'application/json'})

    def data_dir(self):
        self._require_configured()
        return BUILDOUT_DIR.joinpath('var/solr/%s/data' % self.core)

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
        """Create a backup named 'bak-{name}'.
        """
        self._require_configured()
        backup_name = 'bak-{}'.format(name)

        # When the backup exists, delete it. Solr can't do that.
        backup_path = BUILDOUT_DIR.joinpath(
            'var', 'solr', self.core, 'data', 'snapshot.{}'.format(backup_name))
        if backup_path.exists():
            backup_path.rmtree()

        # First, trigger solr commit so that changes are written to disk.
        self.session.get(url=self.base_url + '/update?commit=true').raise_for_status()

        response = self.session.get(url=self.base_url + '/replication',
                                    params={'command': 'backup', 'name': backup_name})
        try:
            response.raise_for_status()
        except Exception:
            print response.json()
            raise
        return response

    def backup_status(self):
        """Check for the progress of a running backup operation.
        """
        self._require_configured()
        response = self.session.get(url=self.base_url + '/replication',
                                    params={'command': 'details'})
        try:
            response.raise_for_status()
        except Exception:
            print response.json()
            raise
        response_data = response.json()

        details = response_data.get('details', {})
        if 'backup' not in details:
            # Status endpoint may not know about running backup yet
            return 'unknown'

        backup_details = details.get('backup', {})

        if 'status' not in backup_details:
            raise Exception("Unexpected backup details response from Solr - "
                            "don't know how to parse %r" % response_data)

        return backup_details['status']

    def restore_backup(self, name):
        """Restore a backup. `name` refers to the backup name.
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

        return response_data['restorestatus']

    def await_backuped(self, timeout=60, interval=0.1):
        """Block until the solr server has no backup in progress.
        """
        for index in range(int(timeout / interval)):
            status = self.backup_status()

            if status == u'success':
                # XXX: Deal with Solr replication API race condition:
                #
                # Status responses from the Solr replication API have a
                # race condition - the backup might already show status
                # 'success' even though Solr hasn't finished writing it to
                # disk yet.
                #
                # We could possibly solve this better by expecting a specific
                # list of files to be written, and checking that the Solr
                # process doesn't have any open file handles any more in
                # the snapshot directory.
                time.sleep(1)
                return

            time.sleep(interval)

        raise ValueError('Timeout ({}s) while waiting for backup to finish.'.format(timeout))

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
    SolrReplicationAPIClient.get_instance().configure(port, core, 'localhost')
    server = SolrServer.get_instance().configure(port, core)

    server.start()
    print '... starting'
    server.await_ready(verbose=True)
    print '... solr output:'
    server.print_tail(max_lines=10)
    print '... stopping'
    server.stop()
    print '... finished'
