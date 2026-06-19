import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')


class ContentBasedRecommender:
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.movie_features = None
        self.similarity_matrix = None
        self.tfidf_matrix = None
        self.vectorizer = None

    def build_genre_features(self):
        print("Building genre features...")

        genre_matrix = self.data_loader.get_movie_genre_matrix()
        scaler = StandardScaler()
        self.movie_features = scaler.fit_transform(genre_matrix)

        print(f"Genre features built! Shape: {self.movie_features.shape}")
        return self.movie_features

    def build_text_features(self):
        print("Building text features...")

        movies_df = self.data_loader.movies.copy()
        genre_cols = self.data_loader.genre_list
        movies_df['genres_text'] = movies_df[genre_cols].apply(
            lambda x: ' '.join([genre_cols[i] for i, val in enumerate(x) if val == 1]),
            axis=1
        )

        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(movies_df['genres_text'])

        print(f"Text features built! Shape: {self.tfidf_matrix.shape}")
        return self.tfidf_matrix

    def calculate_similarity(self, method='cosine'):
        print(f"Calculating similarity using {method}...")

        if method == 'cosine':
            if self.tfidf_matrix is not None:
                self.similarity_matrix = cosine_similarity(self.tfidf_matrix)
            elif self.movie_features is not None:
                self.similarity_matrix = cosine_similarity(self.movie_features)
            else:
                raise ValueError("Build features first!")
        else:
            raise ValueError("Method not supported!")

        print(f"Similarity matrix calculated! Shape: {self.similarity_matrix.shape}")
        return self.similarity_matrix

    def get_similar_movies(self, movie_id, n=10):
        if self.similarity_matrix is None:
            self.build_genre_features()
            self.calculate_similarity()

        movie_idx = self.data_loader.movies[self.data_loader.movies['movie_id'] == movie_id].index
        if len(movie_idx) == 0:
            print(f"Movie {movie_id} not found!")
            return []

        movie_idx = movie_idx[0]

        similarity_scores = list(enumerate(self.similarity_matrix[movie_idx]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        similarity_scores = similarity_scores[1:n + 1]

        similar_movies = []
        for idx, score in similarity_scores:
            movie_id_sim = self.data_loader.movies.iloc[idx]['movie_id']
            title = self.data_loader.get_movie_title(movie_id_sim)
            genres = self.data_loader.get_movie_genres(movie_id_sim)
            avg_rating = self.data_loader.get_average_rating(movie_id_sim)
            year = self.data_loader.get_movie_year(movie_id_sim)

            similar_movies.append({
                'movie_id': movie_id_sim,
                'title': title,
                'year': year,
                'genres': genres,
                'similarity_score': score,
                'avg_rating': avg_rating
            })

        return similar_movies

    def get_user_recommendations(self, user_id, n=10, genre=None, year=None, min_rating=0):
        user_ratings = self.data_loader.get_user_ratings(user_id)

        if len(user_ratings) == 0:
            print(f"User {user_id} has no ratings!")
            return self.data_loader.get_popular_movies(n, genre, year, min_rating)

        high_rated = user_ratings[user_ratings['rating'] >= 4]['movie_id'].tolist()

        if len(high_rated) == 0:
            return self.data_loader.get_popular_movies(n, genre, year, min_rating)

        all_similar = {}
        for movie_id in high_rated[:5]:
            similar = self.get_similar_movies(movie_id, n=5)
            for movie in similar:
                movie_id_sim = movie['movie_id']
                if movie_id_sim not in all_similar:
                    all_similar[movie_id_sim] = 0
                all_similar[movie_id_sim] += movie['similarity_score']

        sorted_movies = sorted(all_similar.items(), key=lambda x: x[1], reverse=True)

        # Apply filters
        filtered_movies = self.data_loader.filter_movies(genre, year, min_rating)
        filtered_ids = filtered_movies['movie_id'].tolist()

        recommendations = []
        for movie_id, score in sorted_movies[:n]:
            if movie_id not in filtered_ids:
                continue

            title = self.data_loader.get_movie_title(movie_id)
            genres = self.data_loader.get_movie_genres(movie_id)
            avg_rating = self.data_loader.get_average_rating(movie_id)
            year_movie = self.data_loader.get_movie_year(movie_id)

            recommendations.append({
                'movie_id': movie_id,
                'title': title,
                'year': year_movie,
                'genres': genres,
                'similarity_score': score,
                'avg_rating': avg_rating
            })

        return recommendations[:n]

    def prepare_content_features(self):
        self.build_genre_features()
        self.build_text_features()
        self.calculate_similarity()
        return self.similarity_matrix