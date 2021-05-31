
def raise_for_api_request(request, exc):
    if not request.get("error_as_message"):
        raise exc
