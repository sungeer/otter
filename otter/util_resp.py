from flask import Response
from werkzeug.http import HTTP_STATUS_CODES

from otter.util_json import dict_to_json_stream


class BaseResponse:

    def __init__(self):
        self.status = True
        self.error_code = None
        self.message = None
        self.data = None

    def to_dict(self):
        resp_dict = {
            'status': self.status,
            'error_code': self.error_code,
            'message': self.message,
            'data': self.data
        }
        return resp_dict


class JsonExtendResponse(Response):

    def __init__(self, response, **kwargs):
        json_response = dict_to_json_stream(response)
        super().__init__(json_response, mimetype='application/json', **kwargs)


def jsonify(*args, **kwargs):
    if args and kwargs:
        raise TypeError('jsonify() behavior undefined when passed both args and kwargs')
    elif len(args) == 1:
        content = args[0]
    else:
        content = args or kwargs
    response = BaseResponse()
    response.data = content
    response = response.to_dict()
    return JsonExtendResponse(response)


def abort(error_code, message=None):
    if not message:
        message = HTTP_STATUS_CODES.get(error_code)
    response = BaseResponse()
    response.status = False
    response.error_code = error_code
    response.message = message
    response = response.to_dict()
    return JsonExtendResponse(response)
