from src.data_loader import MovieDataLoader

# بارگذاری دیتاست
loader = MovieDataLoader('data/ml-100k/')
movies, ratings, users = loader.load_all_data()

# تست چندتا تابع
print("\n🎬 چند فیلم محبوب:")
popular = loader.get_popular_movies(5)
for i, movie in enumerate(popular, 1):
    print(f"{i}. {movie['title']} - امتیاز: {movie['avg_rating']:.2f} ({movie['num_ratings']} نظر)")

# تست یه فیلم خاص
print("\n🎥 اطلاعات فیلم 50:")
info = loader.get_movie_info(50)
if info:
    print(f"عنوان: {info['title']}")
    print(f"ژانرها: {', '.join(info['genres'])}")
    print(f"میانگین امتیاز: {info['avg_rating']:.2f}")

