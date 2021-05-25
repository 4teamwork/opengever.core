

def is_api_request(request):
    if request.getHeader("Accept") == 'application/json':
        return True
    return False


def raise_for_api_request(request, exc):
    if is_api_request(request):
        raise exc
