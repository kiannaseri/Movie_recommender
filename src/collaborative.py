import pandas as pd
import numpy as np
from surprise import SVD, KNNBaseline, NMF, Dataset, Reader
from surprise.model_selection import train_test_split, cross_validate
from surprise import accuracy
import joblib
import os
import warnings

warnings.filterwarnings('ignore')


class CollaborativeFiltering:
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.models = {}
        self.trained_models = {}
        self.predictions = {}
        self.rmse_scores = {}

    def train_svd(self, n_factors=100, n_epochs=20, lr_all=0.005, reg_all=0.02):
        print("Training SVD model...")

        data = self.data_loader.prepare_surprise_data()
        trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

        model = SVD(n_factors=n_factors, n_epochs=n_epochs,
                    lr_all=lr_all, reg_all=reg_all, random_state=42)
        model.fit(trainset)

        predictions = model.test(testset)
        rmse = accuracy.rmse(predictions)

        self.models['svd'] = model
        self.trained_models['svd'] = model
        self.predictions['svd'] = predictions
        self.rmse_scores['svd'] = rmse

        print(f"SVD model trained! RMSE: {rmse:.4f}")
        return model, rmse

    def train_knn(self, k=40, sim_options=None):
        print("Training KNN model...")

        if sim_options is None:
            sim_options = {
                'name': 'pearson_baseline',
                'user_based': False
            }

        data = self.data_loader.prepare_surprise_data()
        trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

        model = KNNBaseline(k=k, sim_options=sim_options)
        model.fit(trainset)

        predictions = model.test(testset)
        rmse = accuracy.rmse(predictions)

        self.models['knn'] = model
        self.trained_models['knn'] = model
        self.predictions['knn'] = predictions
        self.rmse_scores['knn'] = rmse

        print(f"KNN model trained! RMSE: {rmse:.4f}")
        return model, rmse

    def train_nmf(self, n_factors=15, n_epochs=50):
        print("Training NMF model...")

        data = self.data_loader.prepare_surprise_data()
        trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

        model = NMF(n_factors=n_factors, n_epochs=n_epochs, random_state=42)
        model.fit(trainset)

        predictions = model.test(testset)
        rmse = accuracy.rmse(predictions)

        self.models['nmf'] = model
        self.trained_models['nmf'] = model
        self.predictions['nmf'] = predictions
        self.rmse_scores['nmf'] = rmse

        print(f"NMF model trained! RMSE: {rmse:.4f}")
        return model, rmse

    def get_user_recommendations(self, user_id, model_name='svd', n=10, genre=None, year=None, min_rating=0):
        if model_name not in self.trained_models:
            print(f"Model {model_name} not found!")
            return []

        model = self.trained_models[model_name]

        # Get filtered movies
        filtered_movies = self.data_loader.filter_movies(genre, year, min_rating)
        all_movies = filtered_movies['movie_id'].tolist()

        # Get user rated movies
        user_rated = self.data_loader.get_user_ratings(user_id)['movie_id'].tolist()
        unrated_movies = [m for m in all_movies if m not in user_rated]

        # Predict ratings
        predictions = []
        for movie_id in unrated_movies:
            pred = model.predict(user_id, movie_id)
            predictions.append({
                'movie_id': movie_id,
                'predicted_rating': pred.est,
                'title': self.data_loader.get_movie_title(movie_id),
                'year': self.data_loader.get_movie_year(movie_id),
                'genres': self.data_loader.get_movie_genres(movie_id),
                'avg_rating': self.data_loader.get_average_rating(movie_id)
            })

        predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)
        return predictions[:n]

    def get_best_model(self):
        if not self.rmse_scores:
            return None, None

        best_model_name = min(self.rmse_scores, key=self.rmse_scores.get)
        return best_model_name, self.rmse_scores[best_model_name]

    def save_model(self, model_name, filepath='models/'):
        if model_name not in self.trained_models:
            print(f"Model {model_name} not found!")
            return False

        os.makedirs(filepath, exist_ok=True)
        filename = os.path.join(filepath, f'{model_name}_model.pkl')
        joblib.dump(self.trained_models[model_name], filename)
        print(f"Model {model_name} saved to {filename}")
        return True

    def load_model(self, model_name, filepath='models/'):
        filename = os.path.join(filepath, f'{model_name}_model.pkl')
        if not os.path.exists(filename):
            print(f"File {filename} not found!")
            return None

        model = joblib.load(filename)
        self.trained_models[model_name] = model
        print(f"Model {model_name} loaded from {filename}")
        return model


def train_all_models(data_loader):
    cf = CollaborativeFiltering(data_loader)
    cf.train_svd()
    cf.train_knn()
    cf.train_nmf()

    best_model, best_rmse = cf.get_best_model()
    print(f"\nBest model: {best_model} with RMSE: {best_rmse:.4f}")

    return cf