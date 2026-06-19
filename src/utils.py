import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


def save_model(model, model_name, filepath='models/'):
    os.makedirs(filepath, exist_ok=True)
    filename = os.path.join(filepath, f'{model_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pkl')
    joblib.dump(model, filename)
    print(f"Model saved to {filename}")
    return filename


def load_model(filename):
    if not os.path.exists(filename):
        print(f"File {filename} not found!")
        return None
    model = joblib.load(filename)
    print(f"Model loaded from {filename}")
    return model


def get_user_stats(data_loader, user_id):
    user_ratings = data_loader.get_user_ratings(user_id)

    if len(user_ratings) == 0:
        return {
            'user_id': user_id,
            'num_ratings': 0,
            'avg_rating': 0,
            'min_rating': 0,
            'max_rating': 0,
            'favorite_genres': []
        }

    stats = {
        'user_id': user_id,
        'num_ratings': len(user_ratings),
        'avg_rating': user_ratings['rating'].mean(),
        'min_rating': user_ratings['rating'].min(),
        'max_rating': user_ratings['rating'].max()
    }

    favorite_movies = user_ratings[user_ratings['rating'] >= 4]['movie_id'].tolist()
    genre_counter = {}

    for movie_id in favorite_movies:
        genres = data_loader.get_movie_genres(movie_id)
        for genre in genres:
            genre_counter[genre] = genre_counter.get(genre, 0) + 1

    sorted_genres = sorted(genre_counter.items(), key=lambda x: x[1], reverse=True)
    stats['favorite_genres'] = [genre for genre, count in sorted_genres[:5]]

    return stats


def validate_user_id(user_id, data_loader):
    if user_id not in data_loader.users['user_id'].values:
        return False
    return True


def validate_movie_id(movie_id, data_loader):
    if movie_id not in data_loader.movies['movie_id'].values:
        return False
    return True


def get_all_user_ids(data_loader):
    return data_loader.users['user_id'].tolist()


def get_all_movie_ids(data_loader):
    return data_loader.movies['movie_id'].tolist()