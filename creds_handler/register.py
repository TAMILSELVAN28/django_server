
import hashlib
import json
import jwt
import time

from django.http import HttpResponse, JsonResponse
from movie_collections.models import Users


def login(request):
    if request.method != "POST":
        return HttpResponse(status=405, reason="method not allowed")

    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")

    try:
        user = Users.objects.get(name=username)
    except Exception:
        user = Users.objects.create(name=username, password=hashlib.md5(password.encode('utf-8')).hexdigest())
        user.save()

    if user and user.password == hashlib.md5(password.encode('utf-8')).hexdigest():
        auth_token = generate_jwt(username)
        return JsonResponse({'access_token': auth_token}, status=200)
    else:
        return JsonResponse({'message': 'Wrong credentials'}, status=400)
    
    return HttpResponse(status=400, reason="Bad request")

def authenticate(token):
    try:
        payload = decode_jwt(token)
    except Exception:
        return ""
    username = payload['username']
    return username
    

def generate_jwt(username):
    payload = {
        "username": username,
        "iat": int(time.time()),
        "exp": int(time.time() + 86400)
    }
    return jwt.encode(
        payload,
        "a random, long, sequence of characters that only the server knows",
        algorithm='HS256').decode('utf-8')

def decode_jwt(token):
    return jwt.decode(
        token,
        "a random, long, sequence of characters that only the server knows",
        algorithm='HS256')