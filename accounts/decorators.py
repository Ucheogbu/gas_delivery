from functools import wraps
from accounts.models import APIKey
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import JSONRenderer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def check_key(view_func):
    @wraps(view_func)
    def check_key_wrapper(request, **kwargs):
        headers = request.headers
        print(headers)
        api_key =  headers.get('authorization', None)
        if not api_key:
            return JsonResponse(status=401, data="The request you have made requires authentication")
        else:
            if not APIKey.objects.filter(api_key=api_key):
                return JsonResponse(status=401, data="The request you have made requires authentication")
            else:
                key = APIKey.objects.get(api_key=api_key)
                user = key.user
                request.user = user
                return view_func(request, **kwargs)
    return check_key_wrapper