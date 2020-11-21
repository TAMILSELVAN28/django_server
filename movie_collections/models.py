from django.db import models

# Create your models here.

class Users(models.Model):
    name = models.CharField(primary_key=True, max_length=200)
    password = models.CharField(max_length=200)

    class Meta:
        db_table = 'users'

class Collections(models.Model):
    uuid = models.CharField(primary_key=True, max_length=200)
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'collections'

class Movies(models.Model):
    uuid = models.CharField(primary_key=True, max_length=200)
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    genres = models.TextField(default=None, null=True)

    class Meta:
        db_table = 'movies'

class UsersCollections(models.Model):
    users = models.ForeignKey(Users, on_delete=models.CASCADE)
    collections = models.ForeignKey(Collections, on_delete=models.CASCADE)

    class Meta:
        db_table = 'users_collections'

class UsersFavouriteGenres(models.Model):
    users = models.ForeignKey(Users, on_delete=models.CASCADE)
    genres = models.CharField(null=False, max_length=200)
    favorites = models.IntegerField(default=0)

    class Meta:
        db_table = 'users_favourite_genres'

class CollectionsMovies(models.Model):
    collections = models.ForeignKey(Collections, on_delete=models.CASCADE)
    movies = models.ForeignKey(Movies, on_delete=models.CASCADE)

    class Meta:
        db_table = 'collections_movies'

class RequestCount(models.Model):
    id = models.AutoField(primary_key=True)
    request_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'request_count'