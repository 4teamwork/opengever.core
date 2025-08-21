# Create a Zope configuration file (zope.conf) from environment variables

import os
import sys


def to_bool(string):
    if string.lower() in ['on', '1', 'true', 'yes', 'enabled']:
        return True
    return False


def parse_filestorage_options(value):
    res = {}
    filestorages = value.split(';')
    for filestorage in filestorages:
        storage_options = filestorage.split(',')
        if storage_options:
            storage_name = storage_options[0]
            kwargs = dict([kwarg.split('=') for kwarg in storage_options[1:]])
            res[storage_name] = {
                k.replace('-', '_'): v for k, v in kwargs.items()}
    return res


def main():
    if len(sys.argv) < 2:
        sys.exit("Location for Zope configuration file required.")
    zope_conf_file = sys.argv[1]

    env = os.environ
    options = {
        'debug_mode': env.get('DEBUG_MODE', 'off'),
        'security_implementation': env.get('SECURITY_IMPLEMENTATION', 'C'),
        'verbose_security': env.get('VERBOSE_SECURITY', 'off'),
        'zodb_cache_size': env.get('ZODB_CACHE_SIZE', 100000),
        'zserver_threads': env.get('ZSERVER_THREADS', 1),
        'zeo_address': env.get('ZEO_ADDRESS', 'zeoserver:8100'),
        'storage': env.get('STORAGE', 'zeoclient'),
        'read_only': env.get('READ_ONLY', 'false'),
        'shared_blob_dir': env.get('SHARED_BLOB_DIR', 'on'),
        'blob_cache_size': env.get('BLOB_CACHE_SIZE', '2GB')
    }

    if to_bool(options['debug_mode']):
        # Avoid duplicate log entries on console
        options['logfile_loglevel'] = 'CRITICAL'
    else:
        options['logfile_loglevel'] = 'INFO'

    if to_bool(options['verbose_security']):
        options['security_implementation'] = 'python'

    if options['storage'] == 'zeoclient':
        if to_bool(options['shared_blob_dir']):
            blob_dir = '/data/blobstorage'
        else:
            blob_dir = '/app/var/blobcache'
        zodb_main_storage = ZEO_STORAGE_TEMPLATE.format(
            name='main',
            blob_dir=blob_dir,
            zeoclient_name='zeostorage',
            zeoclient_storage='1',
            mountpoint='/',
            **options)
        filestorages = env.get('ADDITIONAL_FILESTORAGES')
        if filestorages:
            for storage_name, storage_options in parse_filestorage_options(
                filestorages
            ).items():
                if to_bool(storage_options.get('shared_blob_dir', 'on')):
                    blob_dir = '/data/blobstorage-{}'.format(storage_name)
                else:
                    blob_dir = '/app/var/blobcache-{}'.format(storage_name)
                default_options = {
                    'zodb_cache_size': options['zodb_cache_size'],
                    'zeo_address': options['zeo_address'],
                    'read_only': 'false',
                    'blob_dir': blob_dir,
                    'shared_blob_dir': 'on',
                    'blob_cache_size': '2GB',
                    'zeoclient_name': '{}_zeostorage'.format(storage_name),
                    'zeoclient_storage': storage_name,
                    'mountpoint': '/{}'.format(storage_name),
                }
                default_options.update(storage_options)
                zodb_main_storage += '\n'
                zodb_main_storage += ZEO_STORAGE_TEMPLATE.format(
                    name=storage_name, **default_options)

    elif options['storage'] == 'relstorage':
        zodb_main_storage = relstorage_config(options)
    else:
        zodb_main_storage = FILESTORAGE_TEMPLATE.format(
            name='main',
            path='/data/filestorage/Data.fs',
            blob_dir='/data/blobstorage',
            mountpoint='/',
            **options)
        if not os.path.exists('/data/filestorage'):
            os.mkdir('/data/filestorage')
        if not os.path.exists('/data/blobstorage'):
            os.mkdir('/data/blobstorage')
        filestorages = env.get('ADDITIONAL_FILESTORAGES')
        if filestorages:
            for storage_name, storage_options in parse_filestorage_options(
                filestorages
            ).items():
                default_options = {
                    'zodb_cache_size': options['zodb_cache_size'],
                    'path': '/data/filestorage/Data.fs',
                    'blob_dir': '/data/blobstorage-{}'.format(storage_name),
                    'mountpoint': '/{}'.format(storage_name),
                }
                default_options.update(storage_options)
                zodb_main_storage += '\n'
                zodb_main_storage += FILESTORAGE_TEMPLATE.format(
                    name=storage_name, **default_options)

    zope_conf = ZOPE_CONF_TEMPLATE.format(
        zodb_main_storage=zodb_main_storage, **options)

    with open(zope_conf_file, 'w') as file_:
        file_.write(zope_conf)


def relstorage_config(options):
    db_adapter = os.environ.get('RELSTORAGE_ADAPTER', 'postgresql')
    relstorage_keys = [
        key for key in os.environ.keys()
        if key.startswith('RELSTORAGE_')
        and not key.startswith('RELSTORAGE_DB_')
        and not key == 'RELSTORAGE_ADAPTER'
    ]
    relstorage_options = ''
    for key in relstorage_keys:
        value = os.environ[key]
        relstorage_options += '        {} {}\n'.format(
            key[11:].lower().replace('_', '-'), value)

    relstorage_db_keys = [
        key for key in os.environ.keys() if key.startswith('RELSTORAGE_DB_')]
    relstorage_db_options = ''
    for key in relstorage_db_keys:
        value = os.environ[key]
        relstorage_db_options += '            {} {}\n'.format(
            key[14:].lower().replace('_', '-'), value)

    return RELSTORAGE_TEMPLATE.format(
        db_adapter=db_adapter,
        relstorage_options=relstorage_options,
        relstorage_db_options=relstorage_db_options,
        **options)


ZOPE_CONF_TEMPLATE = """\
instancehome /app
clienthome /app/var/instance
debug-mode {debug_mode}
security-policy-implementation {security_implementation}
verbose-security {verbose_security}
default-zpublisher-encoding utf-8
http-header-max-length 8192
zserver-threads {zserver_threads}
python-check-interval 1000
pid-filename /app/var/instance.pid
lock-filename /app/var/instance.lock
enable-product-installation off
datetime-format international
trusted-proxy 127.0.0.1

<eventlog>
  level INFO
  <logfile>
    path /app/var/log/instance.log
    level {logfile_loglevel}
  </logfile>
</eventlog>

<http-server>
  address 8080
</http-server>

<zodb_db temporary>
    <temporarystorage>
      name temporary storage for sessioning
    </temporarystorage>
    mount-point /temp_folder
    container-class Products.TemporaryFolder.TemporaryContainer
</zodb_db>

{zodb_main_storage}

%import collective.taskqueue
<taskqueue />
<taskqueue-server />
"""

ZEO_STORAGE_TEMPLATE = """\
<zodb_db {name}>
    cache-size {zodb_cache_size}
    <zeoclient>
      read-only {read_only}
      read-only-fallback false
      blob-dir {blob_dir}
      shared-blob-dir {shared_blob_dir}
      blob-cache-size {blob_cache_size}
      server {zeo_address}
      storage {zeoclient_storage}
      name {zeoclient_name}
      cache-size 128MB
    </zeoclient>
    mount-point {mountpoint}
</zodb_db>
"""

FILESTORAGE_TEMPLATE = """\
<zodb_db {name}>
    cache-size {zodb_cache_size}
    <blobstorage>
      blob-dir {blob_dir}
      <filestorage>
        path {path}
      </filestorage>
    </blobstorage>
    mount-point {mountpoint}
</zodb_db>
"""

RELSTORAGE_TEMPLATE = """\
<zodb_db main>
    cache-size {zodb_cache_size}
    %import relstorage
    <relstorage>
{relstorage_options}
        <{db_adapter}>
{relstorage_db_options}
        </{db_adapter}>
    </relstorage>
    mount-point /
</zodb_db>
"""

if __name__ == "__main__":
    main()
