import simplejson
from django.http import HttpResponse

class ApiResponse(HttpResponse):
    def __init__(self, data):
        response = simplejson.dumps(data)
        super(ApiResponse, self).__init__(response, content_type='text/javascript')


class ApiError(ApiResponse):
    def __init__(self, error_message):
        super(ApiError, self).__init__({'success': False, 'error': error_message})


class ApiSuccess(ApiResponse):
    def __init__(self, additional_data=None):
        response = {'success': True}
        if additional_data:
            response['data'] = additional_data
        super(ApiSuccess, self).__init__(response)

