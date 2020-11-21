from movie_collections.models import (
    Collections, CollectionsMovies, Movies,
    UsersCollections, UsersFavouriteGenres,
)
import pandas as pd
import uuid

from movie_collections.movies_ops import fetch_movies, update_fav, process_fav


def fetch_collections(username, col_id=None):
    # Fetch user collection from sql
    collection_obj = Collections.objects.filter(
        userscollections__users_id=username).values('uuid', 'title', 'description')

    if col_id:
        collection_obj = collection_obj.filter(uuid=col_id)

    df = pd.DataFrame(collection_obj)
    return df

def store_collections(username, req_data):
    title = req_data['title']
    description = req_data['description']
    col_id = str(uuid.uuid4())

    # Create Collection
    col_obj = Collections.objects.create(uuid=col_id, title=title, description=description)
    col_obj.save()
    movies_df = pd.DataFrame(req_data['movies'])
    bulk_col_movies = []

    # Add movies in Bulk
    for _, movie in movies_df.iterrows():
        # create movie if not exist
        mov_obj = Movies.objects.get_or_create(uuid=movie['uuid'], title=movie['title'], description=movie['description'], genres=movie['genres'])
        col_mov = CollectionsMovies(collections_id=col_id, movies_id=movie['uuid'])
        bulk_col_movies.append(col_mov)
    
    # Update user favourits
    update_fav(username, movies_df)

    # Link collection and movies list
    CollectionsMovies.objects.bulk_create(bulk_col_movies)

    # Create collection belongs to respective user
    user_col = UsersCollections.objects.create(collections_id=col_id, users_id=username)
    user_col.save()

    return col_id

def modify_collections(username, request, col_id):
    # Fetch required data from request
    update_col_title = request['title']
    update_col_description = request['description']
    update_movies_df = pd.DataFrame(request['movies'])

    # Fetch existing movie details
    existing_movie_df = fetch_movies(username, col_id)

    # update collections details
    Collections.objects.filter(uuid=col_id).update(title=update_col_title, description=update_col_description)

    # modify_df is existing movie in collections got updated
    modify_df = update_movies_df.loc[update_movies_df.uuid.isin(existing_movie_df.uuid)]
    # new_movies_df is newly added movie into the collections
    new_movies_df = update_movies_df.loc[~update_movies_df.uuid.isin(existing_movie_df.uuid)]
    # delete_movies_df is existing movies got removed from collections
    delete_movies_df = existing_movie_df.loc[~existing_movie_df.uuid.isin(update_movies_df.uuid)]

    new_genres_modified = []
    old_genres_modified = []

    # Update Existing movies
    for x, movie in modify_df.iterrows():
        mov_obj = Movies.objects.get(uuid=movie['uuid'])
        mov_obj.title = movie['title']
        mov_obj.description = movie['description']

        if mov_obj.genres != movie['genres']: 
            mov_obj.genres = movie['genres']
            new_genres_modified.append(movie['genres'])
            old_genres_modified.append(mov_obj.genres)

        mov_obj.save()

    # Modify favourite genres based on movie updates
    new_genres_modified_df = pd.DataFrame(new_genres_modified, columns=['genres'])
    old_genres_modified_df = pd.DataFrame(old_genres_modified, columns=['genres'])
    delete_count_df = process_fav(old_genres_modified_df)

    # Add new movies in Bulk
    bulk_col_movies = []
    for _,movie in new_movies_df.iterrows():
        # create movie if not exist
        mov_obj = Movies.objects.get_or_create(uuid=movie['uuid'], title=movie['title'], description=movie['description'], genres=movie['genres'])
        col_mov = CollectionsMovies(collections_id=col_id, movies_id=movie['uuid'])
        bulk_col_movies.append(col_mov)

    # Update user favourite genres for new movies
    new_movies_df = pd.concat([new_movies_df, new_genres_modified_df], ignore_index=True, sort=False)
    update_fav(username, new_movies_df)

    # Link collection and movies list
    CollectionsMovies.objects.bulk_create(bulk_col_movies)

    # Remove deleted movies from collection list
    if not delete_movies_df.empty:
        delete_movie_id_list = delete_movies_df['uuid'].tolist()
        mov_obj = Movies.objects.filter(uuid__in=delete_movie_id_list).values('genres')
        genre_df = pd.DataFrame(mov_obj)
        delte_fav_genre_df = process_fav(genre_df)
        delte_fav_genre_df = pd.concat([delte_fav_genre_df, delete_count_df], ignore_index=True, sort=False)

        # Delete Movie from users collections
        CollectionsMovies.objects.filter(collections_id=col_id).filter(movies_id__in=delete_movie_id_list).delete()
    else:
        delte_fav_genre_df = delete_count_df.copy()

    # Update Favourite Movie geners based on movie delete
    for _, user_generes in delte_fav_genre_df.iterrows():
        user_obj = UsersFavouriteGenres.objects.get(users_id=username, genres=user_generes['favorites'])
        user_obj.favorites = user_obj.favorites - user_generes['genres']
        user_obj.save()
