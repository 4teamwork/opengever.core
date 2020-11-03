import os


def debug_modified_out_of_sync_env_var_is_set():
    return bool(os.environ.get('GEVER_DEBUG_MODIFIED_OUF_OF_SYNC'))
