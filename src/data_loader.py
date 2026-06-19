import pandas as pd
import numpy as np
import os
from surprise import Dataset, Reader
import warnings

warnings.filterwarnings('ignore')


class MovieDataLoader:
    def __init__(self, data_path='data/ml-100k/'):
        self.data_path = data_path
        self.movies = None
        self.ratings = None
        self.users = None
        self.movie_titles = None
        self.genre_list = None

    def load_all_data(self):
        print("Loading MovieLens dataset...")

        columns = ['movie_id', 'title', 'release_date', 'video_release_date',
                   'IMDb_URL', 'unknown', 'Action', 'Adventure', 'Animation',
                   'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy',
                   'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi',
                   'Thriller', 'War', 'Western']

        self.movies = pd.read_csv(
            os.path.join(self.data_path, 'u.item'),
            sep='|',
            encoding='latin-1',
            names=columns
        )

        self.ratings = pd.read_csv(
            os.path.join(self.data_path, 'u.data'),
            sep='\t',
            names=['user_id', 'movie_id', 'rating', 'timestamp']
        )

        user_columns = ['user_id', 'age', 'gender', 'occupation', 'zip_code']
        self.users = pd.read_csv(
            os.path.join(self.data_path, 'u.user'),
            sep='|',
            names=user_columns
        )

        genre_cols = ['unknown', 'Action', 'Adventure', 'Animation', 'Children',
                      'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy',
                      'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance',
                      'Sci-Fi', 'Thriller', 'War', 'Western']
        self.genre_list = genre_cols
        self.movie_titles = self.movies[['movie_id', 'title']].copy()

        # Extract year from title
        self.movies['year'] = self.movies['title'].str.extract(r'\((\d{4})\)').astype(float)

        print(f"Loaded successfully!")
        print(f"   - {len(self.movies)} movies")
        print(f"   - {len(self.ratings)} ratings")
        print(f"   - {len(self.users)} users")

        return self.movies, self.ratings, self.users

    def get_movie_genres(self, movie_id):
        movie = self.movies[self.movies['movie_id'] == movie_id]
        if len(movie) == 0:
            return []
        genres = []
        for genre in self.genre_list:
            if movie[genre].values[0] == 1:
                genres.append(genre)
        return genres

    def get_movie_title(self, movie_id):
        movie = self.movies[self.movies['movie_id'] == movie_id]
        if len(movie) > 0:
            return movie['title'].values[0]
        return None

    def get_movie_year(self, movie_id):
        movie = self.movies[self.movies['movie_id'] == movie_id]
        if len(movie) > 0:
            return movie['year'].values[0]
        return None

    def get_user_ratings(self, user_id):
        return self.ratings[self.ratings['user_id'] == user_id]

    def get_movie_ratings(self, movie_id):
        return self.ratings[self.ratings['movie_id'] == movie_id]

    def get_average_rating(self, movie_id):
        ratings = self.get_movie_ratings(movie_id)
        if len(ratings) > 0:
            return ratings['rating'].mean()
        return 0

    def get_all_genres(self):
        return [g for g in self.genre_list if g != 'unknown']

    def get_all_years(self):
        years = self.movies['year'].dropna().unique()
        years = sorted(years, reverse=True)
        return [int(y) for y in years]

    def prepare_surprise_data(self):
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(
            self.ratings[['user_id', 'movie_id', 'rating']],
            reader
        )
        return data

    def get_movie_genre_matrix(self):
        return self.movies[self.genre_list].values

    def get_movie_features(self):
        return self.movies[self.genre_list].values

    def filter_movies(self, genre=None, year=None, min_rating=0):
        filtered = self.movies.copy()

        if genre and genre != 'All':
            filtered = filtered[filtered[genre] == 1]

        if year:
            filtered = filtered[filtered['year'] == year]

        if min_rating > 0:
            movie_ids = filtered['movie_id'].tolist()
            valid_movies = []
            for movie_id in movie_ids:
                avg_rating = self.get_average_rating(movie_id)
                if avg_rating >= min_rating:
                    valid_movies.append(movie_id)
            filtered = filtered[filtered['movie_id'].isin(valid_movies)]

        return filtered

    def get_popular_movies(self, n=10, genre=None, year=None, min_rating=0):
        filtered = self.filter_movies(genre, year, min_rating)

        if len(filtered) == 0:
            return []

        movie_ratings = self.ratings[self.ratings['movie_id'].isin(filtered['movie_id'])]
        movie_ratings = movie_ratings.groupby('movie_id')['rating'].agg(['count', 'mean'])
        movie_ratings = movie_ratings.sort_values(['count', 'mean'], ascending=False)
        popular_movies = movie_ratings.head(n).index.tolist()

        result = []
        for movie_id in popular_movies:
            title = self.get_movie_title(movie_id)
            avg_rating = movie_ratings.loc[movie_id, 'mean']
            num_ratings = movie_ratings.loc[movie_id, 'count']
            year = self.get_movie_year(movie_id)
            genres = self.get_movie_genres(movie_id)

            result.append({
                'movie_id': movie_id,
                'title': title,
                'year': year,
                'genres': genres,
                'avg_rating': avg_rating,
                'num_ratings': num_ratings
            })
        return result

    def get_movie_info(self, movie_id):
        movie = self.movies[self.movies['movie_id'] == movie_id]
        if len(movie) == 0:
            return None

        genres = self.get_movie_genres(movie_id)
        avg_rating = self.get_average_rating(movie_id)

        return {
            'movie_id': movie_id,
            'title': movie['title'].values[0],
            'year': movie['year'].values[0] if not pd.isna(movie['year'].values[0]) else None,
            'genres': genres,
            'avg_rating': avg_rating,
            'release_date': movie['release_date'].values[0] if 'release_date' in movie.columns else None
        }


def load_movielens(data_path='data/ml-100k/'):
    loader = MovieDataLoader(data_path)
    return loader.load_all_data()