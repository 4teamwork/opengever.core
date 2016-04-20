import hashlib


def file_checksum(filename, chunksize=65536):
    """Calculates a checksum for the given file."""
    h = hashlib.md5()
    with open(filename, 'rb') as f:
        chunk = f.read(chunksize)
        while len(chunk) > 0:
            h.update(chunk)
            chunk = f.read(chunksize)
        return u'MD5', h.hexdigest()
