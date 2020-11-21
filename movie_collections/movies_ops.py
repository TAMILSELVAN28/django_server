from movie_collections.models import (
    UsersCollections, UsersFavouriteGenres,
)
import numpy as np
import pandas as pd


def fetch_movies(username, col_id):
    # Fetch user movies collections from sql
    movies_obj = UsersCollections.objects.filter(users_id=username).filter(
        collections__collectionsmovies__collections_id=col_id).values(
            'collections__collectionsmovies__movies__uuid',
            'collections__collectionsmovies__movies__title',
            'collections__collectionsmovies__movies__description',
            'collections__collectionsmovies__movies__genres'
    )
    df = pd.DataFrame(movies_obj).rename(
        columns = {
            'collections__collectionsmovies__movies__uuid': 'uuid',
            'collections__collectionsmovies__movies__title': 'title',
            'collections__collectionsmovies__movies__description': 'description',
            'collections__collectionsmovies__movies__genres': 'genres'
        }
    )
    return df

def process_fav(movies_df):
    # Prepare data for genres and count unique genres
    fav_gen_df = pd.DataFrame()
    if movies_df.empty:
        return fav_gen_df
    movies_df = movies_df[['genres']]
    movies_df = movies_df.apply(lambda x : x.replace("", np.nan))
    movies_df = movies_df.dropna()
    if not movies_df.empty:
        movies_df['genres'] = movies_df['genres'].apply(lambda x : x.split(","))
        fav_gen_df = movies_df.explode('genres').reset_index(drop=True)
        fav_gen_df = fav_gen_df[['genres']]
        fav_gen_df = fav_gen_df.genres.value_counts()
        fav_gen_df = pd.DataFrame(fav_gen_df)
        fav_gen_df = fav_gen_df.reset_index()
        fav_gen_df = fav_gen_df.rename(columns={"index": "favorites"})
    return fav_gen_df

def update_fav(username, movies_df):
    # Update movie favourite count based on movie list added
    fav_gen_df = process_fav(movies_df)
    for _, user_generes in fav_gen_df.iterrows():
        user_obj, is_created = UsersFavouriteGenres.objects.get_or_create(users_id=username, genres=user_generes['favorites'])
        if is_created:
            user_obj.favorites = user_generes['genres']
        else:
            user_obj.favorites = user_obj.favorites + user_generes['genres']
        user_obj.save()

