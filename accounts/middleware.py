from django.http import JsonResponse
from accounts.models import UserData

def check_api_key(get_response):
    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        headers = request.headers
        api_key =  headers.get('authorization', None)
        print(api_key)
        if not api_key:
            return  JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Incomplete data: authorization(API-Key) not found cannot be null'})
        else:
            if not UserData.objects.filter(api_key=api_key):
                return  JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Incomplete data: authorization(API-Key) is invalid'})
            else:
                userdata = UserData.objects.get(api_key=api_key)
                user = userdata.user            

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware

class CheckApi:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        headers = request.headers
        api_key =  headers.get('authorization', None)
        print(api_key)
        if not api_key:
            return  JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Incomplete data: authorization(API-Key) not found cannot be null'})
        else:
            if not UserData.objects.filter(api_key=api_key):
                return  JsonResponse({'response_code': 400, 'response_status': 'error', 'message': f'Incomplete data: authorization(API-Key) is invalid'})
            else:
                userdata = UserData.objects.get(api_key=api_key)
                user = userdata.user            

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

