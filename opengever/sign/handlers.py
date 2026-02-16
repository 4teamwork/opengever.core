from opengever.sign.sign import Signer


def reset_sign_data_after_clone(document, event):
    Signer(document).clear()
