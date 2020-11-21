import json
from django.test import TestCase, Client
from django.urls import reverse

from movie_collections.models import Collections, Movies, UsersFavouriteGenres, CollectionsMovies, Users, UsersCollections, RequestCount
from movie_collections.factories import UsersFactory, CollectionsFactory
from rest_framework.test import APIRequestFactory
from rest_framework import status

client = Client()


class CollectionTestCase(TestCase):
    def setUp(self):
        self.access_token = self.registeruser()
        self.col_id = self.add_collection()

    def registeruser(self):
        user = UsersFactory.build()
        response = client.post(reverse('login'), data=json.dumps({"username": user.name, "password": user.password}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.json()

    def add_collection(self):
        col = CollectionsFactory.build()
        data = {
            "title": col.title,
            "description": col.description,
            "movies": [
                {
                    "title": "test movie",
                    "description": "test movie description",
                    "genres": "Action",
                    "uuid": "s1dk2sldk8-dss1d-3sdsd0s"
                }
            ]
        }
        headers = {'HTTP_AUTHORIZATION': self.access_token['access_token']}
        response = client.post(reverse('collection'), data=json.dumps(data), content_type='application/json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.json()

    def get_collection(self):
        col = CollectionsFactory.build()
        data = {
            "title": col.title,
            "description": col.description,
            "movies": [
                {
                    "title": "test movie",
                    "description": "test movie description",
                    "genres": "Action",
                    "uuid": "s1dk2sldk8-dss1d-3sdsd0s"
                }
            ]
        }
        headers = {'HTTP_AUTHORIZATION': self.access_token['access_token']}
        response = client.get(reverse('collection'), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
