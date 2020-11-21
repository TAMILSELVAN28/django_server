from re import sub

from django.http import HttpResponse, JsonResponse
from json import dumps, loads
from datetime import datetime

from movie_collections.models import Users, RequestCount
from creds_handler.register import authenticate


class AuthenticatorMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request) 
        response = self.get_response(request)
        return response

    def process_request(self, request):
        req_count = RequestCount.objects.get_or_create(id=1)
        RequestCount.objects.filter(id=1).update(request_count=req_count[0].request_count + 1)
        return None

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        request_path = request.path

        if request_path == "/register/":
            return None

        token = request.headers.get('Authorization', None)
        if not token:
            print('Authorization header not set')
            return HttpResponse(status=400)
        try:
            username = authenticate(token)
            user = Users.objects.get(name=username)
            if not user:
                return HttpResponse(status=401)
        except Exception as e:
            return HttpResponse(status=401)

        request_data = dict()
        request_data["username"] = username
        content_type = request.headers.get('Content-Type', '')

        if 'application/json' in content_type:
            org_request_data = getattr(request, '_body', request.body)
            if org_request_data:
                org_request_data = loads(org_request_data)
            else:
                org_request_data = dict()
            org_request_data['middleware'] = request_data

            request._body = dumps(org_request_data)
        elif 'form-data' in content_type:
            org_request_data = request.POST.copy()
            org_request_data.__setitem__('middleware', request_data)
            request.POST = org_request_data
            data = dict()
            data['middleware'] = request_data
            request._body = dumps(data)
        else:
            data = dict()
            data['middleware'] = request_data
            request._body = dumps(data)
        return None
