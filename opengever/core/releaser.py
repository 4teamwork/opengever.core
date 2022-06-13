import logging
import os.path
import re
import sys


logger = logging.getLogger("opengever.releaser")


VERSIONS_FILE_NAME = "versions.cfg"


def _make_versions_file_path(data):
    """Return versions file path. Validate file exists."""

    repo_root_path = data["reporoot"]
    versions_file_path = os.path.join(repo_root_path, VERSIONS_FILE_NAME)

    if not os.path.exists(versions_file_path):
        logger.critical("Could not find 'versions.cfg' at '{}'.".format(
            repo_root_path))
        sys.exit(1)

    return versions_file_path


def _read_versions_file(data):
    with open(_make_versions_file_path(data), 'r') as fp:
        return fp.read()


def _write_versions_file(data, text):
    with open(_make_versions_file_path(data), 'w') as fp:
        fp.write(text)


def on_prerelease_middle(data):
    """Write new gever version to versions.cfg before creating a release.

    Insert the version pinning at the top of the [versions] section.
    """
    versions_file = _read_versions_file(data)

    if "[versions]" not in versions_file:
        logger.critical("Could not find '[versions]' section in file "
                        "'{}'.".format(VERSIONS_FILE_NAME))
        sys.exit(1)

    if "opengever.core" in versions_file:
        logger.critical("Unexpectedly found pinning for 'opengever.core' in "
                        "file '{}'.".format(VERSIONS_FILE_NAME))
        sys.exit(1)

    new_version = data["new_version"]
    versions_file_with_pinning = versions_file.replace(
        "[versions]\n",
        "[versions]\nopengever.core = {}\n\n".format(
            new_version))

    _write_versions_file(data, versions_file_with_pinning)
    logger.info("Pinned opengever.core to '{}' in '{}'".format(
        new_version, VERSIONS_FILE_NAME))


def on_postrelease_middle(data):
    """Remove pinned gever version after release."""

    versions_file = _read_versions_file(data)

    if "opengever.core" not in versions_file:
        logger.critical("Could not find pinning for 'opengever.core' in "
                        "file '{}'.".format(VERSIONS_FILE_NAME))
        sys.exit(1)

    versions_file_without_pinning = re.sub(
        "^opengever.core = .*$\n*", "", versions_file, flags=re.MULTILINE)

    _write_versions_file(data, versions_file_without_pinning)
    logger.info("Removed pinning of opengever.core in '{}'".format(
        VERSIONS_FILE_NAME))
