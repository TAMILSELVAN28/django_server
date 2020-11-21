import factory
import itertools
import random
import string

from movie_collections.models import (
    Collections, CollectionsMovies, Movies,
    Users, UsersCollections, UsersFavouriteGenres,
    RequestCount
)

def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))

class UsersFactory(factory.Factory):
    class Meta:
        model = Users

    name = factory.Sequence(lambda n: 'john%s%s%s' % (n,n,n))
    password = factory.LazyAttribute(lambda o: '%s' % random_string())

class CollectionsFactory(factory.Factory):
    class Meta:
        model = Collections

    title = factory.Sequence(lambda n: '%sjohn%s%s%s' % (n, n, n, n))
    description = factory.LazyAttribute(lambda o: '%s' % random_string(100))