"""Focused unit tests for model-selection helpers."""
from src.collaborative import CollaborativeFiltering
from src.hybrid import HybridRecommender


def test_best_model_returns_lowest_rmse():
    recommender = CollaborativeFiltering.__new__(CollaborativeFiltering)
    recommender.rmse_scores = {"svd": 0.94, "knn": 0.88, "nmf": 1.02}

    assert recommender.get_best_model() == ("knn", 0.88)


def test_best_model_returns_none_before_training():
    recommender = CollaborativeFiltering.__new__(CollaborativeFiltering)
    recommender.rmse_scores = {}

    assert recommender.get_best_model() == (None, None)


def test_hybrid_alpha_is_clamped_to_valid_range():
    recommender = HybridRecommender.__new__(HybridRecommender)

    recommender.set_alpha(1.5)
    assert recommender.alpha == 1

    recommender.set_alpha(-0.2)
    assert recommender.alpha == 0


def test_hybrid_alpha_accepts_boundary_values():
    recommender = HybridRecommender.__new__(HybridRecommender)

    recommender.set_alpha(0)
    assert recommender.alpha == 0

    recommender.set_alpha(1)
    assert recommender.alpha == 1
