from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response
    if isinstance(response.data, dict) and 'detail' in response.data:
        response.data = {'ok': False, 'detail': response.data.get('detail')}
    elif isinstance(response.data, dict):
        response.data = {'ok': False, 'errors': response.data}
    else:
        response.data = {'ok': False, 'detail': response.data}
    return response

