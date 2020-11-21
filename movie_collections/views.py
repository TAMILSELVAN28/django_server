from movie_collections.models import (
    Collections, CollectionsMovies, Movies,
    Users, UsersCollections, UsersFavouriteGenres,
    RequestCount
)
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from movie_collections.collection_ops import fetch_collections, store_collections, modify_collections
from movie_collections.movies_ops import fetch_movies

import json
import os

import pandas as pd
import requests


# client configs
demo_client = os.environ.get('demo_client')
demo_client_secret = os.environ.get('demo_client_secret')

def movies(request):
    if request.method != 'GET':
        return HttpResponse(status=400, reason="Method not allowed")

    # Get page request query params
    page = request.GET.get("page", 1)
    try:
        # Fetch movies list from endpoint
        url = 'http://demo.credy.in/api/v1/maya/movies/'
        request_url = url + f"?page={page}"
        r = requests.get(request_url, auth=(demo_client,demo_client_secret))
        if r.status_code == 200:
            result = r.json()
            is_success = result.get('is_success', True)
            if is_success:
                result["data"] = result.pop("results")
            else:
                result = {}
            return JsonResponse(result, status=200)
        else:
            HttpResponse(status=400, reason="Bad Request")

    except Exception:
        return HttpResponse(status=400, reason="Bad Request")

def collection(request):
    # Fetch all collections for particular user
    if request.method == 'GET':
        try:
            # Fetch input from request
            req_data = json.loads(request.body)
            username = req_data['middleware']['username']

            # Fetch collections data
            result = fetch_collections(username)
            collection_data = result.to_dict('records')

            # Fetch users favourite genres
            user_obj = UsersFavouriteGenres.objects.filter(users_id=username).values('genres').order_by('favorites').reverse()[0:3]
            favourite_genres = pd.DataFrame(user_obj)
            favourite_genres_list = favourite_genres['genres'].tolist()
            if favourite_genres_list:
                favourite_genres = str(favourite_genres_list)[1:-1]
            else:
                favourite_genres_list = ""

            output = {
                "is_success": True,
                "data": {
                    "collections": collection_data
                },
                "favourite_genres": favourite_genres
            }
            return JsonResponse(output, status=200)

        except Exception as e:
            return HttpResponse(status=400, reason="Bad Request")

    # Store collections for particular user
    elif request.method == 'POST':
        try:
            req_data = json.loads(request.body)
            username = req_data['middleware']['username']
            col_id = store_collections(username, req_data)
            result = {
                "collection_uuid": col_id
            }
            return JsonResponse(result, status=200)
        except Exception as e:
            return HttpResponse(status=400, reason="Bad Request")

    return HttpResponse(status=400, reason="Method not allowed")

# Functions to fetch, update and delete particular collection
def update_collections(request, collection_id):
    req_data = json.loads(request.body)
    username = req_data['middleware']['username']

    # Fetch collection details
    if request.method == 'GET':
        try:
            col_df = fetch_collections(username, collection_id)
            if not col_df.empty:
                movies_df = fetch_movies(username, collection_id)
                col_output = col_df.to_dict('records')[0]
                movies_dict = movies_df.to_dict('records')
                result = {
                    'title': col_output['title'],
                    'description': col_output['description'],
                    'movies': movies_dict
                }
                return JsonResponse(result, status=200)
            else:
                return HttpResponse(status=400, reason="Invalid request wrong collection_uuid")

        except Exception as e:
            return HttpResponse(status=400, reason="Bad Requestd")

    # Update collection
    elif request.method == 'POST':
        try:
            req_data = json.loads(request.body)
            col = Collections.objects.filter(uuid=collection_id).filter(userscollections__users_id=username)
            if col:
                modify_collections(username, req_data, collection_id)
                result = {
                    "message": "collection updated successfully"
                }
                return JsonResponse(result, status=200)
            else:
                return HttpResponse(status=400, reason="Invalid request wrong collection_uuid")

        except Exception as e:
            return HttpResponse(status=400, reason="Bad Request")

    # Delete collection
    elif request.method == 'DELETE':
        try:
            col = Collections.objects.filter(uuid=collection_id).filter(userscollections__users_id=username)
            if col:
                col.delete()
                result = {
                    "message": "collection deleted successfully"
                }
                return JsonResponse(result, status=200)
            else:
                return HttpResponse(status=400, reason="Invalid request wrong collection_uuid")
        except Exception:
            return HttpResponse(status=400, reason="Bad Request")

    return HttpResponse(status=400, reason="Method not allowed")

# Function to fetch server request count
def request_count(request):
    if request.method != 'GET':
        return HttpResponse(status=400, reason="Method not allowed")

    try:
        req_count_obj = RequestCount.objects.get(id=1)
        result = {
            "requests": req_count_obj.request_count
        }
        return JsonResponse(result, status=200)
    except Exception:
        return HttpResponse(status=400, reason="Bad Request")

# Function to reset server request count
def reset_request_count(request):
    if request.method != 'POST':
        return HttpResponse(status=400, reason="Method not allowed")

    try:
        req_count_obj = RequestCount.objects.get(id=1)
        RequestCount.objects.filter(id=1).update(request_count=0)
        result = {
            "message": "request count reset successfully"
        }
        return JsonResponse(result, status=200)
    except Exception:
        return HttpResponse(status=400, reason="Bad Request")
