from base64 import b64decode
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from datetime import datetime
import struct


MAX_AGE = 20 * 60 * 10000000  # 20 minutes (.NET DateTime.UtcNow.Ticks)


def int2bytes(n):
    """Converts an integer into a bytestring in big-endian byte order."""
    return struct.pack('>I', n)


def long2bytes(l):
    """Converts a long integer into a bytestring in big-endian byte order."""
    return struct.pack('>Q', l)


def generate_key(modulus, exp):
    """Generate a public key from modulus and exponent."""
    modulus = int(b64decode(modulus).encode('hex'), 16)
    exp = int(b64decode(exp).encode('hex'), 16)
    return RSAPublicNumbers(exp, modulus).public_key(default_backend())


def create_message(access_token, url, timestamp):
    access_token_length = int2bytes(len(access_token))
    url_length = int2bytes(len(url))
    timestamp = long2bytes(int(timestamp))
    timestamp_length = int2bytes(len(timestamp))
    return (
        access_token_length
        + access_token
        + url_length
        + url.upper()
        + timestamp_length
        + timestamp
    )


def validate_wopi_proof(access_token, url, timestamp, proof_key,
                        current_signature, old_signature):
    """Verifies the timestamp and the signature of a signed WOPI request."""
    if not validate_timestamp(timestamp):
        return False

    current_key = generate_key(proof_key['@modulus'], proof_key['@exponent'])
    old_key = generate_key(proof_key['@oldmodulus'], proof_key['@oldexponent'])

    message = create_message(access_token, url, timestamp)

    return (
        validate_signature(message, current_signature, current_key)
        or validate_signature(message, old_signature, current_key)
        or validate_signature(message, current_signature, old_key)
    )


def validate_timestamp(timestamp):
    timestamp = int(timestamp)
    # .NET DateTime.UtcNow.Ticks: 100-nanosecond intervals that have elapsed
    # since 12:00:00 midnight, January 1, 0001, UTC
    current_timestamp = int(
        (datetime.utcnow() - datetime(1, 1, 1)).total_seconds() * 10000000)
    if timestamp < current_timestamp - MAX_AGE:
        return False
    return True


def validate_signature(message, signature, public_key):
    signature = b64decode(signature)
    try:
        public_key.verify(
            signature, message, padding.PKCS1v15(), hashes.SHA256())
        return True
    except InvalidSignature:
        return False
