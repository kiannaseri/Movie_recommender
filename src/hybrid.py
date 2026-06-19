import numpy as np
import pandas as pd
from src.collaborative import CollaborativeFiltering
from src.content_based import ContentBasedRecommender
import warnings

warnings.filterwarnings('ignore')


class HybridRecommender:
    def __init__(self, data_loader, cf_model=None, cb_model=None):
        self.data_loader = data_loader
        self.cf_model = cf_model
        self.cb_model = cb_model
        self.alpha = 0.5

    def set_models(self, cf_model, cb_model):
        self.cf_model = cf_model
        self.cb_model = cb_model

    def set_alpha(self, alpha):
        self.alpha = max(0, min(1, alpha))

    def get_hybrid_recommendations(self, user_id, n=10, alpha=None, genre=None, year=None, min_rating=0):
        if alpha is None:
            alpha = self.alpha

        # Get filtered movies
        filtered_movies = self.data_loader.filter_movies(genre, year, min_rating)
        filtered_ids = filtered_movies['movie_id'].tolist()

        # Get CF recommendations
        cf_recommendations = []
        if self.cf_model is not None:
            cf_results = self.cf_model.get_user_recommendations(user_id, model_name='svd', n=n * 2)
            for movie in cf_results:
                if movie['movie_id'] in filtered_ids:
                    cf_recommendations.append({
                        'movie_id': movie['movie_id'],
                        'cf_score': movie['predicted_rating'],
                        'title': movie['title'],
                        'year': movie['year'],
                        'genres': movie['genres'],
                        'avg_rating': movie['avg_rating']
                    })

        # Get CB recommendations
        cb_recommendations = []
        if self.cb_model is not None:
            cb_results = self.cb_model.get_user_recommendations(user_id, n=n * 2, genre=genre, year=year,
                                                                min_rating=min_rating)
            for movie in cb_results:
                cb_recommendations.append({
                    'movie_id': movie['movie_id'],
                    'cb_score': movie.get('similarity_score', 0),
                    'title': movie['title'],
                    'year': movie['year'],
                    'genres': movie['genres'],
                    'avg_rating': movie['avg_rating']
                })

        # Combine results
        if len(cf_recommendations) == 0 and len(cb_recommendations) == 0:
            return self.data_loader.get_popular_movies(n, genre, year, min_rating)
        elif len(cf_recommendations) == 0:
            return cb_recommendations[:n]
        elif len(cb_recommendations) == 0:
            return cf_recommendations[:n]

        # Combine scores
        combined_scores = {}
        cf_dict = {item['movie_id']: item['cf_score'] for item in cf_recommendations}
        cb_dict = {item['movie_id']: item['cb_score'] for item in cb_recommendations}

        cf_max = max(cf_dict.values()) if cf_dict else 1
        cb_max = max(cb_dict.values()) if cb_dict else 1

        all_movie_ids = set(cf_dict.keys()) | set(cb_dict.keys())

        for movie_id in all_movie_ids:
            cf_score = cf_dict.get(movie_id, 0) / cf_max if cf_max > 0 else 0
            cb_score = cb_dict.get(movie_id, 0) / cb_max if cb_max > 0 else 0

            hybrid_score = alpha * cf_score + (1 - alpha) * cb_score
            combined_scores[movie_id] = hybrid_score

        sorted_movies = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

        recommendations = []
        for movie_id, score in sorted_movies[:n]:
            title = self.data_loader.get_movie_title(movie_id)
            genres = self.data_loader.get_movie_genres(movie_id)
            avg_rating = self.data_loader.get_average_rating(movie_id)
            year_movie = self.data_loader.get_movie_year(movie_id)

            recommendations.append({
                'movie_id': movie_id,
                'title': title,
                'year': year_movie,
                'genres': genres,
                'hybrid_score': score,
                'avg_rating': avg_rating,
                'cf_score': cf_dict.get(movie_id, 0),
                'cb_score': cb_dict.get(movie_id, 0)
            })

        return recommendations