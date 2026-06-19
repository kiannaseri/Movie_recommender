import re
import random
from datetime import datetime
import requests
import json


class MovieChatbot:
    def __init__(self, data_loader=None):
        self.data_loader = data_loader
        self.context = {}
        self.conversation_history = []

        # Greetings
        self.greetings = [
            "Hello! 👋 I'm your Movie Assistant!",
            "Hi there! 🎬 How can I help you today?",
            "Hey! 🤖 Ready to find some great movies?",
            "Greetings! 🌟 I know everything about movies!"
        ]

        self.farewells = [
            "Goodbye! 🎬 Enjoy watching!",
            "See you later! 🍿 Don't forget to rate movies!",
            "Bye! 🌟 Come back for more recommendations!",
            "Take care! 🎥 Happy movie watching!"
        ]

        self.help_responses = [
            "I can help you with:\n"
            "• 🎭 Find movies by genre (Action, Comedy, etc.)\n"
            "• 📅 Search by year (1995, 2000, etc.)\n"
            "• ⭐ Filter by rating (4 stars and above)\n"
            "• 📊 Get movie recommendations\n"
            "• 🎬 Get details about specific movies\n\n"
            "Just type what you're looking for! 🎯"
        ]

        self.weather_responses = [
            "I'm a movie expert, not a weatherman! ☀️\n"
            "But I can recommend movies for rainy days! 🎬",
            "Weather? I only know about movies! 🌟\n"
            "How about a movie instead? 🎥"
        ]

    def set_data_loader(self, data_loader):
        """Set data loader for movie queries"""
        self.data_loader = data_loader

    def process_query(self, query):
        """Main entry point for processing user queries"""
        query_lower = query.lower().strip()

        # Check for empty query
        if not query_lower:
            return "Please ask me something! 🎬"

        # Check for greeting
        if self.is_greeting(query_lower):
            return random.choice(self.greetings)

        # Check for farewell
        if self.is_farewell(query_lower):
            return random.choice(self.farewells)

        # Check for help
        if self.is_help(query_lower):
            return random.choice(self.help_responses)

        # Check for date/time
        if self.is_date_query(query_lower):
            return self.get_date_response()

        # Check for weather
        if self.is_weather_query(query_lower):
            return random.choice(self.weather_responses)

        # Check for genre list
        if self.is_genre_list_query(query_lower):
            return self.get_genre_list()

        # Check for movie recommendations
        if self.is_recommendation_query(query_lower):
            return self.get_recommendations(query_lower)

        # Check for movie info
        if self.is_movie_info_query(query_lower):
            return self.get_movie_info(query_lower)

        # Check for random movie
        if self.is_random_movie_query(query_lower):
            return self.get_random_movie()

        # Check for popular movies
        if self.is_popular_query(query_lower):
            return self.get_popular_movies(query_lower)

        # Default response
        return self.get_default_response(query_lower)

    def is_greeting(self, text):
        greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning',
                     'good afternoon', 'good evening', 'howdy', 'sup', 'yo']
        return any(g in text for g in greetings)

    def is_farewell(self, text):
        farewells = ['bye', 'goodbye', 'see you', 'later', 'cya', 'take care',
                     'exit', 'quit', 'end', 'stop']
        return any(f in text for f in farewells)

    def is_help(self, text):
        helps = ['help', 'what can you do', 'capabilities', 'how to use',
                 'guide', 'tutorial', 'what do you do']
        return any(h in text for h in helps)

    def is_date_query(self, text):
        dates = ['date', 'today', 'day', 'what day', 'what is the date',
                 'time', 'current time', 'now']
        return any(d in text for d in dates)

    def is_weather_query(self, text):
        weathers = ['weather', 'rain', 'sun', 'temperature', 'hot', 'cold',
                    'forecast', 'climate', 'cloud']
        return any(w in text for w in weathers)

    def is_genre_list_query(self, text):
        genres_keywords = ['what genres', 'list genres', 'show genres',
                           'genres available', 'movie types', 'categories']
        return any(g in text for g in genres_keywords)

    def is_recommendation_query(self, text):
        rec_keywords = ['recommend', 'suggest', 'find', 'search', 'show me',
                        'give me', 'looking for', 'want to watch']
        return any(r in text for r in rec_keywords)

    def is_movie_info_query(self, text):
        info_keywords = ['about', 'info', 'details', 'tell me about',
                         'what is', 'movie called']
        return any(i in text for i in info_keywords)

    def is_random_movie_query(self, text):
        random_keywords = ['random movie', 'surprise me', 'anything',
                           'don\'t care', 'any movie']
        return any(r in text for r in random_keywords)

    def is_popular_query(self, text):
        popular_keywords = ['popular', 'top', 'best', 'highest rated',
                            'most rated', 'trending']
        return any(p in text for p in popular_keywords)

    def get_date_response(self):
        now = datetime.now()
        return f"📅 Today is {now.strftime('%A, %B %d, %Y')}\n⏰ Current time: {now.strftime('%H:%M:%S')}\n🎬 Perfect time for a movie!"

    def get_genre_list(self):
        if not self.data_loader:
            return "Please load the dataset first! 📊"

        genres = self.data_loader.get_all_genres()
        return f"🎭 Available genres:\n" + "• " + "\n• ".join(genres)

    def get_recommendations(self, query):
        if not self.data_loader:
            return "Please load the dataset first! 📊"

        # Extract filters from query
        genre = self.extract_genre(query)
        year = self.extract_year(query)
        rating = self.extract_rating(query)
        count = self.extract_count(query)

        # Get recommendations
        try:
            recs = self.data_loader.get_popular_movies(
                n=count,
                genre=genre,
                year=year,
                min_rating=rating if rating else 0
            )

            if not recs:
                return "No movies found with your criteria! 🎬\nTry different filters."

            response = f"🎬 Found {len(recs)} movies:\n\n"
            for i, movie in enumerate(recs[:count], 1):
                title = movie['title'][:50]
                rating_val = movie['avg_rating']
                genres = ', '.join(movie['genres'][:3])
                year_val = movie.get('year', 'N/A')

                response += f"{i}. {title}\n"
                response += f"   🎭 {genres}\n"
                response += f"   📅 {year_val} | ⭐ {rating_val:.1f}/5\n\n"

            return response

        except Exception as e:
            return f"Error getting recommendations: {str(e)}"

    def get_movie_info(self, query):
        if not self.data_loader:
            return "Please load the dataset first! 📊"

        # Try to find movie title in query
        movie_title = self.extract_movie_title(query)

        if not movie_title:
            return "Please specify a movie title! 🎬"

        # Search for movie
        movies = self.data_loader.movies
        found = movies[movies['title'].str.contains(movie_title, case=False, na=False)]

        if len(found) == 0:
            return f"Movie '{movie_title}' not found! Try another title. 🎬"

        if len(found) > 1:
            titles = [f"{i + 1}. {row['title']}" for i, row in found.head(5).iterrows()]
            return f"Found multiple movies:\n" + "\n".join(titles)

        movie_id = found.iloc[0]['movie_id']
        info = self.data_loader.get_movie_info(movie_id)

        if not info:
            return "Movie details not available! 🎬"

        response = f"🎬 {info['title']}\n"
        response += "=" * 40 + "\n"
        response += f"📅 Year: {info['year'] if info['year'] else 'N/A'}\n"
        response += f"🎭 Genres: {', '.join(info['genres'])}\n"
        response += f"⭐ Rating: {info['avg_rating']:.2f}/5\n"

        ratings = self.data_loader.get_movie_ratings(movie_id)
        response += f"📊 Votes: {len(ratings)}\n"

        return response

    def get_random_movie(self):
        if not self.data_loader:
            return "Please load the dataset first! 📊"

        import random
        movie_id = random.choice(self.data_loader.movies['movie_id'].tolist())
        info = self.data_loader.get_movie_info(movie_id)

        if not info:
            return "Could not find a random movie! 🎬"

        return f"🎲 Surprise Movie:\n\n" \
               f"🎬 {info['title']}\n" \
               f"🎭 {', '.join(info['genres'])}\n" \
               f"⭐ {info['avg_rating']:.2f}/5\n" \
               f"📅 {info['year'] if info['year'] else 'N/A'}"

    def get_popular_movies(self, query):
        if not self.data_loader:
            return "Please load the dataset first! 📊"

        count = self.extract_count(query)
        genre = self.extract_genre(query)

        popular = self.data_loader.get_popular_movies(
            n=count,
            genre=genre
        )

        if not popular:
            return "No popular movies found! 🎬"

        response = f"🔥 Top {len(popular)} Popular Movies:\n\n"
        for i, movie in enumerate(popular[:count], 1):
            response += f"{i}. {movie['title'][:50]}\n"
            response += f"   ⭐ {movie['avg_rating']:.1f} | 🎭 {', '.join(movie['genres'][:3])}\n"
            response += f"   📊 {movie['num_ratings']} votes\n\n"

        return response

    def get_default_response(self, query):
        responses = [
            "🤔 I'm not sure about that. Try asking about movies!\n"
            "Example: 'Show me Action movies from 2000'",

            "🎬 I'm a movie expert! Ask me about:\n"
            "• Genres (Action, Comedy, Drama)\n"
            "• Years (1995, 2000, 2010)\n"
            "• Ratings (4 stars and above)\n"
            "• Movie recommendations\n"
            "• Specific movie details",

            "😅 That's outside my movie knowledge!\n"
            "I can help you find movies by genre, year, or rating. Just ask! 🎯",

            "🎥 I don't know about that, but I know MOVIES!\n"
            "Try saying something like 'Recommend action movies' 🍿"
        ]
        return random.choice(responses)

    def extract_genre(self, text):
        """Extract genre from text"""
        if not self.data_loader:
            return None

        genres = self.data_loader.get_all_genres()
        for genre in genres:
            if genre.lower() in text.lower():
                return genre
        return None

    def extract_year(self, text):
        """Extract year from text"""
        year_match = re.search(r'\b(19[0-9]{2}|20[0-9]{2})\b', text)
        if year_match:
            year = int(year_match.group())
            if 1900 <= year <= 2026:
                return year
        return None

    def extract_rating(self, text):
        """Extract minimum rating from text"""
        # Look for patterns like "4 stars", "rating 4", "4.5 rating"
        patterns = [
            r'(\d+\.?\d*)\s*stars?',
            r'rating\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*rating',
            r'(\d+\.?\d*)\s*★',
            r'min\s*(\d+\.?\d*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                rating = float(match.group(1))
                if 0 <= rating <= 5:
                    return rating
        return None

    def extract_count(self, text):
        """Extract number of recommendations"""
        patterns = [
            r'(\d+)\s*movies?',
            r'(\d+)\s*recommendations?',
            r'(\d+)\s*results?',
            r'(\d+)\s*items?',
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                count = int(match.group(1))
                if 1 <= count <= 50:
                    return count

        # Default
        if '10' in text or 'ten' in text:
            return 10
        elif '5' in text or 'five' in text:
            return 5
        elif '20' in text or 'twenty' in text:
            return 20
        elif '30' in text or 'thirty' in text:
            return 30

        return 10  # Default

    def extract_movie_title(self, text):
        """Extract movie title from text"""
        # Look for patterns like "tell me about Movie Name"
        # or "info about Movie Name"
        patterns = [
            r'about\s+([A-Za-z0-9\s]+?)(?:\s+\(|$|\.|\?)',
            r'info\s+([A-Za-z0-9\s]+?)(?:\s+\(|$|\.|\?)',
            r'movie\s+called\s+([A-Za-z0-9\s]+?)(?:\s+\(|$|\.|\?)',
            r'film\s+called\s+([A-Za-z0-9\s]+?)(?:\s+\(|$|\.|\?)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # If no pattern match, try to find a movie title
        if self.data_loader:
            movies = self.data_loader.movies
            # Look for movie titles in text
            for _, row in movies.iterrows():
                title = row['title'].lower()
                if title in text.lower() or text.lower() in title:
                    return row['title']

        return None