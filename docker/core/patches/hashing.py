from ftw.bumblebee.config import bumblebee_config
from ftw.bumblebee.usersalt import get_user_salt
import base64
import hashlib
import hmac
import time


TIME_STEP_WINDOW = 30


def one_time_token(secret, content=''):
    return access_token(secret, content + str(time_step()))


def verify_one_time_token(secret, token, content=''):
    current_step = time_step()
    previous_step = time_step() - 1
    return token in (access_token(secret, content + str(current_step)),
                     access_token(secret, content + str(previous_step)))


def access_token(secret, content):
    digest = hmac.new(secret, content, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest)


def get_derived_secret(salt):
    """
    Compute the bumblebee derived secret from the application secret.

    :param salt: A string used in the computation of the hash.
    :return: The derived secret.
    """
    application_secret = bumblebee_config.secret
    return hashlib.pbkdf2_hmac('sha1', application_secret.encode(),
                               salt=salt.encode(), iterations=1000, dklen=64)


def get_access_token_by_checksum(checksum):
    """Returns the access token for a checksum.
    The access token is used for getting the converted
    document from the bumblebee service.
    """
    return access_token(secret=get_derived_secret(salt='access token'),
                        content=checksum + get_user_salt())


def get_conversion_access_token():
    """The conversion access token is used to authenticate with bumblebee
    when posting a conversion job.
    It is a time based access token.
    """
    return one_time_token(get_derived_secret('one time token'))


def get_demand_job_access_token():
    """The demand job access token is used to authenticate with bumblebee
    when posting a demand job.
    It is a time based access token.
    """
    return one_time_token(get_derived_secret(
        'one time token for demand job'))


def time_step():
    return int(time.time()) / TIME_STEP_WINDOW
