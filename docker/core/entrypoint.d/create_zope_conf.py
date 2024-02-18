# Create a Zope configuration file (zope.conf) from environment variables

import os
import sys


def to_bool(string):
    if string.lower() in ['on', '1', 'true', 'enabled']:
        return True
    return False


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
        'storage': env.get('STORAGE', 'zeoclient')
    }

    if options['debug_mode'] == 'on':
        # Avoid duplicate log entries on console
        options['logfile_loglevel'] = 'CRITICAL'
    else:
        options['logfile_loglevel'] = 'INFO'

    if options['verbose_security'] == 'on':
        options['security_implementation'] = 'python'

    if options['storage'] == 'zeoclient':
        zodb_main_storage = ZEO_STORAGE_TEMPLATE.format(**options)
    elif options['storage'] == 'relstorage':
        zodb_main_storage = relstorage_config(options)
    else:
        zodb_main_storage = FILESTORAGE_TEMPLATE.format(**options)
        if not os.path.exists('/data/filestorage'):
            os.mkdir('/data/filestorage')
        if not os.path.exists('/data/blobstorage'):
            os.mkdir('/data/blobstorage')

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
        relstorage_options += '        {} {}'.format(
            key[11:].lower().replace('_', '-'), value)

    relstorage_db_keys = [
        key for key in os.environ.keys() if key.startswith('RELSTORAGE_DB_')]
    relstorage_db_options = ''
    for key in relstorage_db_keys:
        value = os.environ[key]
        relstorage_db_options += '            {} {}'.format(
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

<logger access>
  level WARN
  <logfile>
    path STDOUT
    format %(message)s
  </logfile>
</logger>

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
<zodb_db main>
    cache-size {zodb_cache_size}
    <zeoclient>
      read-only false
      read-only-fallback false
      blob-dir /data/blobstorage
      shared-blob-dir on
      server {zeo_address}
      storage 1
      name zeostorage
      cache-size 128MB
    </zeoclient>
    mount-point /
</zodb_db>
"""

FILESTORAGE_TEMPLATE = """\
<zodb_db main>
    cache-size {zodb_cache_size}
    <blobstorage>
      blob-dir /data/blobstorage
      <filestorage>
        path /data/filestorage/Data.fs
      </filestorage>
    </blobstorage>
    mount-point /
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
<zodb_db main>
"""

if __name__ == "__main__":
    main()
