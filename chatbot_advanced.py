import re
import random
import json
import os
from datetime import datetime
from collections import defaultdict
import numpy as np


class AdvancedMovieChatbot:
    def __init__(self, data_loader=None):
        self.data_loader = data_loader
        self.context = {}
        self.conversation_history = []
        self.user_preferences = {}
        self.user_mood = "neutral"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.last_topic = None
        self.conversation_count = 0

        # ===== MOVIE TRIVIA & FUN FACTS =====
        self.movie_trivia = [
            "🎬 The first movie ever made was 'Roundhay Garden Scene' in 1888!",
            "🎥 The longest movie ever made is 240 hours long!",
            "🍿 The most expensive movie ever made cost over $400 million!",
            "🎬 The first animated movie was made in 1908!",
            "🎥 The best-selling movie franchise is the Marvel Cinematic Universe!",
            "🍿 The first movie with sound was released in 1927!",
            "🎬 The most awarded movie of all time is 'Ben-Hur' with 11 Oscars!",
            "🎥 The first color movie was made in 1908!",
            "🍿 The shortest movie ever is only 0.5 seconds long!",
            "🎬 The first movie to gross $1 billion was 'Titanic'!",
            "🎥 The oldest movie still in existence is from 1888!",
            "🍿 The most watched movie of all time is 'Avatar'!",
            "🎬 The first movie with CGI was 'Westworld' in 1973!",
        ]

        self.movie_quotes = [
            "🎬 'May the Force be with you.' - Star Wars",
            "🎥 'I'll be back.' - Terminator",
            "🍿 'You can't handle the truth!' - A Few Good Men",
            "🎬 'Here's looking at you, kid.' - Casablanca",
            "🎥 'To infinity and beyond!' - Toy Story",
            "🍿 'Just keep swimming.' - Finding Nemo",
            "🎬 'Why so serious?' - The Dark Knight",
            "🎥 'Hakuna Matata!' - The Lion King",
            "🍿 'Life is like a box of chocolates.' - Forrest Gump",
            "🎬 'Houston, we have a problem.' - Apollo 13",
            "🎥 'I am your father.' - Star Wars",
            "🍿 'There's no place like home.' - The Wizard of Oz",
        ]

        self.movie_jokes = [
            "😂 Why did the movie go to the doctor? Because it had a bad 'plot'!",
            "🎬 Why don't movies ever get lost? Because they always have a good 'plot'!",
            "🤣 What do you call a movie about a sad cow? A 'moo-dy' film!",
            "😂 Why did the actor go to the bank? To get his 'makeup'!",
            "🎥 What do you call a movie that's always late? A 'film' with commitment issues!",
            "🍿 Why did the movie theater serve popcorn? Because it was a 'corny' place!",
        ]

        # ===== MOOD-BASED RECOMMENDATIONS =====
        self.movie_moods = {
            "happy": {
                "genres": ["Comedy", "Animation", "Adventure", "Musical"],
                "message": "🎉 You're in a great mood! Here are some uplifting movies to keep that happiness going!",
                "description": "I detected you're happy! 😊 That's wonderful! Happy people usually enjoy fun, light-hearted movies that make them laugh and feel good."
            },
            "sad": {
                "genres": ["Drama", "Romance", "Documentary", "Film-Noir"],
                "message": "🤗 I know you're feeling down. These heartwarming movies might help you feel better!",
                "description": "😢 I can sense you're feeling a bit sad. When people are sad, they often connect with emotional, deep stories that help them process their feelings."
            },
            "excited": {
                "genres": ["Action", "Adventure", "Sci-Fi", "Thriller"],
                "message": "⚡ Your energy is amazing! Here are some thrilling movies that match your excitement!",
                "description": "🚀 You seem really excited! Excited people usually enjoy fast-paced, action-packed movies that keep them on the edge of their seat!"
            },
            "angry": {
                "genres": ["Action", "Thriller", "War", "Western"],
                "message": "😤 I can see you're a bit frustrated. These movies might help you release that energy!",
                "description": "😠 It seems like you're feeling a bit angry. Sometimes people enjoy intense, action-packed movies when they have a lot of energy to release."
            },
            "romantic": {
                "genres": ["Romance", "Drama", "Musical"],
                "message": "❤️ Feeling romantic? Here are some beautiful love stories!",
                "description": "💕 I can tell you're in a romantic mood! People who feel romantic often enjoy heartwarming love stories and emotional dramas."
            },
            "curious": {
                "genres": ["Documentary", "Mystery", "Sci-Fi"],
                "message": "🔍 You're feeling curious! Here are some thought-provoking movies!",
                "description": "🤔 You seem curious today! Curious people enjoy movies that make them think, mysteries that need solving, and documentaries that teach them something new."
            },
            "bored": {
                "genres": ["Comedy", "Animation", "Adventure", "Action"],
                "message": "🎬 Bored? Let me find something exciting to watch!",
                "description": "😴 You mentioned being bored! When people are bored, they usually want something fun, exciting, and engaging that will keep them entertained!"
            },
            "relaxed": {
                "genres": ["Drama", "Comedy", "Musical", "Animation"],
                "message": "😌 Relaxing mood detected! Here are some chill movies for you!",
                "description": "🧘‍♀️ You seem really relaxed! Relaxed people usually enjoy calming, feel-good movies that are easy to watch and don't require too much thinking."
            },
            "thoughtful": {
                "genres": ["Drama", "Film-Noir", "Documentary", "Mystery"],
                "message": "🤔 Feeling thoughtful? Here are some deep and meaningful movies!",
                "description": "🧠 You seem deep in thought! Thoughtful people often enjoy complex, meaningful movies that explore big ideas and make them reflect."
            }
        }

        # ===== RESPONSES BY MOOD =====
        self.responses_by_mood = {
            "happy": [
                "😊 You're in a great mood! Let me suggest a perfect movie to keep that happiness going!",
                "🎉 I can tell you're happy! Here's a feel-good movie recommendation!",
                "✨ Your positive energy is contagious! I know just the movie for you!",
            ],
            "sad": [
                "🤗 I'm here for you! Movies can be great when you're feeling down.",
                "💕 Sometimes a good movie can brighten your day. Here's something uplifting.",
                "🎬 I know just what you need! A movie that will make you feel better.",
            ],
            "excited": [
                "🚀 I love your excitement! Let me find an action-packed movie for you!",
                "⚡ Ready for some adventure? I've got the perfect recommendation!",
                "🎯 Your energy is amazing! Let me suggest a thrilling movie!",
            ],
            "neutral": [
                "🎬 Let me find the perfect movie for you!",
                "🎥 What kind of movie are you in the mood for?",
                "🍿 I'm here to help you find great movies!",
            ]
        }

        # ===== GREETINGS & FAREWELLS =====
        self.greetings = [
            "👋 Hello! I'm your Movie Assistant! I can help you find the perfect movie!",
            "🎬 Hi there! Ready to discover some amazing films?",
            "🤖 Hey! I know everything about movies! What are you looking for?",
            "🌟 Greetings! I'm here to help you find great movies to watch!",
            "🎥 Welcome! I can recommend movies based on your mood, genre, year, or rating!",
            "🍿 Oh hi! Ready for some movie magic? Let's find you something great!",
        ]

        self.farewells = [
            "👋 Goodbye! May the force be with you!",
            "🎬 See you later! Keep watching great movies!",
            "🌟 Bye! Remember, the best movie is the next one!",
            "🎥 Take care! Happy movie hunting!",
            "🍿 Goodbye! Don't forget to rate the movies you watch!",
        ]

        # ===== HELP SYSTEM =====
        self.help_sections = {
            "overview": {
                "title": "🤖 Movie Assistant Help Guide",
                "description": "I'm your personal Movie Assistant! Here's everything I can do:"
            },
            "categories": {
                "🎭 Find Movies by Genre": {
                    "description": "Ask me for movies in specific genres",
                    "examples": "• 'Show me Action movies'\n• 'Find Comedy films'\n• 'Recommend Drama movies'"
                },
                "📅 Search by Year": {
                    "description": "Find movies released in specific years",
                    "examples": "• 'Movies from 1995'\n• 'Show me films from 2000'\n• 'Recommend 2010 movies'"
                },
                "⭐ Filter by Rating": {
                    "description": "Find movies with high ratings",
                    "examples": "• 'Movies with 4 stars'\n• 'Rating above 4.5'\n• 'Best rated movies'"
                },
                "😊 Mood-Based Recommendations": {
                    "description": "I can recommend movies based on how you feel!",
                    "examples": "• 'I'm happy today'\n• 'I'm feeling sad'\n• 'I'm bored'\n• 'I want something romantic'"
                },
                "🎬 Movie Details": {
                    "description": "Get detailed information about specific movies",
                    "examples": "• 'Tell me about The Matrix'\n• 'Info about Star Wars'\n• 'What is Titanic about?'"
                },
                "🎲 Random Movies": {
                    "description": "Get surprised with random movie suggestions",
                    "examples": "• 'Surprise me!'\n• 'Recommend a random movie'\n• 'Give me anything'"
                },
                "🎮 Games & Entertainment": {
                    "description": "Play movie trivia games and get fun facts!",
                    "examples": "• 'Give me a movie trivia'\n• 'Play a movie quiz'\n• 'Movie fact'\n• 'Tell me a movie quote'\n• 'Tell me a joke'"
                },
                "📊 Compare Movies": {
                    "description": "Compare two movies against each other",
                    "examples": "• 'Compare Star Wars and Star Trek'\n• 'Compare The Godfather and Goodfellas'"
                },
                "🔥 Popular Movies": {
                    "description": "See what's popular and trending",
                    "examples": "• 'Show popular movies'\n• 'Top 10 movies'\n• 'Best movies of all time'"
                }
            },
            "footer": "💡 Just type whatever you want and I'll do my best to help! Try combining filters: 'Action movies from 2000 with 4 stars'"
        }

        self.unknown_responses = [
            "🤔 I'm not sure about that. I'm a Movie Assistant! Try asking me about movies!",
            "😅 I only know about movies! Ask me for recommendations, movie info, or trivia!",
            "🎬 I'm a movie expert! Try saying 'Help' to see everything I can do!",
            "🤖 I may not know about that, but I know MOVIES! What would you like to watch?",
        ]

    def set_data_loader(self, data_loader):
        self.data_loader = data_loader

    def detect_user_mood(self, text):
        """Detect user mood from text"""
        text_lower = text.lower()

        mood_keywords = {
            "happy": ['happy', 'great', 'good', 'excited', 'love', 'awesome', 'wonderful', 'amazing',
                      'joy', 'glad', 'fantastic', 'delighted', 'pleased'],
            "sad": ['sad', 'depressed', 'lonely', 'cry', 'upset', 'terrible', 'bad', 'worried',
                    'miserable', 'heartbroken', 'gloomy', 'down', 'blue', 'melancholy'],
            "excited": ['excited', 'wow', 'cool', 'awesome', 'fantastic', 'amazing',
                        'thrilled', 'pumped', 'energized'],
            "angry": ['angry', 'mad', 'hate', 'annoyed', 'frustrated', 'upset',
                      'irritated', 'furious', 'rage', 'ticked'],
            "romantic": ['romantic', 'love', 'couple', 'date night', 'valentine', 'sweet',
                         'lovely', 'affection', 'heart'],
            "curious": ['curious', 'wonder', 'interesting', 'fascinating', 'learn',
                        'discover', 'explore', 'knowledge'],
            "bored": ['bored', 'nothing', 'something', 'entertain', 'kill time',
                      'pass time', 'anything', 'whatever'],
            "relaxed": ['relaxed', 'chill', 'calm', 'peaceful', 'tranquil', 'easy',
                        'rest', 'zen', 'serene'],
            "thoughtful": ['thoughtful', 'think', 'deep', 'meaningful', 'philosophical',
                           'contemplate', 'reflect', 'ponder']
        }

        mood_scores = defaultdict(int)
        for mood, keywords in mood_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    mood_scores[mood] += 1

        if mood_scores:
            return max(mood_scores.items(), key=lambda x: x[1])[0]
        return "neutral"

    def get_mood_recommendations(self):
        """Get recommendations based on detected mood"""
        mood = self.user_mood
        mood_data = self.movie_moods.get(mood, self.movie_moods.get("neutral", {
            "genres": ["Drama", "Comedy"],
            "message": "🎬 Let me find something great for you!",
            "description": "I'll find the perfect movie for you!"
        }))

        response = f"🧠 **Mood Analysis:** {mood_data.get('description', '')}\n\n"
        response += f"🎯 **Recommendation:** {mood_data.get('message', '')}\n\n"

        if self.data_loader:
            genres = mood_data.get("genres", ["Drama", "Comedy"])
            all_movies = []
            for genre in genres[:3]:
                movies = self.data_loader.get_popular_movies(n=5, genre=genre)
                all_movies.extend(movies)

            seen = set()
            unique_movies = []
            for movie in all_movies:
                if movie['movie_id'] not in seen:
                    seen.add(movie['movie_id'])
                    unique_movies.append(movie)

            if unique_movies:
                response += f"🎬 **Recommended Movies:**\n\n"
                for i, movie in enumerate(unique_movies[:5], 1):
                    response += f"{i}. {movie['title'][:50]}\n"
                    response += f"   🎭 {', '.join(movie['genres'][:3])}\n"
                    response += f"   ⭐ {movie['avg_rating']:.1f}/5\n\n"
            else:
                response += f"🎬 Let me suggest some popular movies instead:\n"
                popular = self.data_loader.get_popular_movies(5)
                for i, movie in enumerate(popular, 1):
                    response += f"{i}. {movie['title'][:50]} ⭐ {movie['avg_rating']:.1f}\n"
        else:
            response += "📊 Please load the dataset first to get movie recommendations!"

        return response

    def get_help_response(self):
        """Get detailed help"""
        response = f"{self.help_sections['overview']['title']}\n"
        response += "=" * 60 + "\n\n"
        response += f"{self.help_sections['overview']['description']}\n\n"

        for category, data in self.help_sections['categories'].items():
            response += f"**{category}**\n"
            response += f"   📖 {data['description']}\n"
            response += f"   💡 Examples:\n"
            for example in data['examples'].split('\n'):
                response += f"      {example}\n"
            response += "\n"

        response += self.help_sections['footer']
        return response

    def get_trivia_game(self):
        """Get a trivia game question"""
        trivia_questions = [
            {
                "question": "🎮 **Movie Trivia Game!**\n\nWhich movie won the most Oscars?",
                "options": ["A) Ben-Hur", "B) Titanic", "C) Avatar", "D) The Godfather"],
                "answer": "A",
                "explanation": "✅ Ben-Hur won 11 Oscars in 1959!"
            },
            {
                "question": "🎮 **Movie Trivia Game!**\n\nWhat was the first animated movie?",
                "options": ["A) Snow White", "B) Toy Story", "C) A Bug's Life", "D) The Little Mermaid"],
                "answer": "A",
                "explanation": "✅ Snow White was the first animated movie in 1937!"
            },
            {
                "question": "🎮 **Movie Trivia Game!**\n\nWho directed 'Inception'?",
                "options": ["A) James Cameron", "B) Christopher Nolan", "C) Steven Spielberg", "D) Martin Scorsese"],
                "answer": "B",
                "explanation": "✅ Christopher Nolan directed 'Inception' in 2010!"
            },
            {
                "question": "🎮 **Movie Trivia Game!**\n\nWhat year was the first movie with sound made?",
                "options": ["A) 1927", "B) 1930", "C) 1920", "D) 1935"],
                "answer": "A",
                "explanation": "✅ 'The Jazz Singer' was the first movie with sound in 1927!"
            },
            {
                "question": "🎮 **Movie Trivia Game!**\n\nWhich movie features the quote 'I'll be back'?",
                "options": ["A) Terminator", "B) Predator", "C) RoboCop", "D) The Matrix"],
                "answer": "A",
                "explanation": "✅ Arnold Schwarzenegger said it in 'The Terminator'!"
            },
            {
                "question": "🎮 **Movie Trivia Game!**\n\nWhat is the highest-grossing movie of all time?",
                "options": ["A) Avatar", "B) Titanic", "C) Star Wars", "D) Avengers: Endgame"],
                "answer": "A",
                "explanation": "✅ 'Avatar' is the highest-grossing movie with $2.8 billion!"
            }
        ]
        return random.choice(trivia_questions)

    def get_fun_response(self, query):
        """Get fun responses"""
        query_lower = query.lower()

        # Trivia
        if any(word in query_lower for word in ['trivia', 'fact', 'did you know', 'interesting']):
            return f"💡 **Movie Fact:**\n{random.choice(self.movie_trivia)}"

        # Quotes
        if any(word in query_lower for word in ['quote', 'dialogue', 'line', 'famous words']):
            return f"🎬 **Famous Movie Quote:**\n{random.choice(self.movie_quotes)}"

        # Jokes
        if any(word in query_lower for word in ['joke', 'funny', 'humor', 'laugh']):
            return f"😂 **Movie Joke:**\n{random.choice(self.movie_jokes)}"

        # Games
        if any(word in query_lower for word in ['game', 'quiz', 'play', 'challenge']):
            game = self.get_trivia_game()
            return f"{game['question']}\n\n{game['options'][0]}\n{game['options'][1]}\n{game['options'][2]}\n{game['options'][3]}\n\n💡 Type 'answer A', 'answer B', 'answer C', or 'answer D' to check!"

        # Compare
        if 'compare' in query_lower and 'and' in query_lower:
            return self.handle_compare(query)

        return None

    def handle_compare(self, query):
        """Compare two movies"""
        match = re.search(r'compare\s+(.+?)\s+and\s+(.+?)(?:\?|$|\.)', query.lower())
        if not match:
            return "Please specify two movies to compare!\nExample: 'Compare Star Wars and Star Trek'"

        movie1 = match.group(1).strip()
        movie2 = match.group(2).strip()

        if not self.data_loader:
            return "Please load the dataset first!"

        movies = self.data_loader.movies
        m1 = movies[movies['title'].str.contains(movie1, case=False, na=False)]
        m2 = movies[movies['title'].str.contains(movie2, case=False, na=False)]

        if len(m1) == 0 or len(m2) == 0:
            return "One or both movies not found! Please check the names."

        m1_info = self.data_loader.get_movie_info(m1.iloc[0]['movie_id'])
        m2_info = self.data_loader.get_movie_info(m2.iloc[0]['movie_id'])

        if not m1_info or not m2_info:
            return "Could not get movie details!"

        m1_ratings = self.data_loader.get_movie_ratings(m1_info['movie_id'])
        m2_ratings = self.data_loader.get_movie_ratings(m2_info['movie_id'])

        response = "🎬 **Movie Comparison:**\n"
        response += "=" * 50 + "\n\n"

        response += f"📌 **{m1_info['title']}**\n"
        response += f"   ⭐ Rating: {m1_info['avg_rating']:.2f}/5 ({len(m1_ratings)} votes)\n"
        response += f"   🎭 Genres: {', '.join(m1_info['genres'][:3])}\n"
        response += f"   📅 Year: {m1_info['year'] if m1_info['year'] else 'N/A'}\n\n"

        response += f"📌 **{m2_info['title']}**\n"
        response += f"   ⭐ Rating: {m2_info['avg_rating']:.2f}/5 ({len(m2_ratings)} votes)\n"
        response += f"   🎭 Genres: {', '.join(m2_info['genres'][:3])}\n"
        response += f"   📅 Year: {m2_info['year'] if m2_info['year'] else 'N/A'}\n\n"

        if m1_info['avg_rating'] > m2_info['avg_rating']:
            response += f"🏆 **Winner:** {m1_info['title']} has a higher rating!\n"
            response += f"   ✨ {m1_info['title']} wins by {(m1_info['avg_rating'] - m2_info['avg_rating']):.2f} points!"
        elif m2_info['avg_rating'] > m1_info['avg_rating']:
            response += f"🏆 **Winner:** {m2_info['title']} has a higher rating!\n"
            response += f"   ✨ {m2_info['title']} wins by {(m2_info['avg_rating'] - m1_info['avg_rating']):.2f} points!"
        else:
            response += f"🤝 **It's a tie!** Both have {m1_info['avg_rating']:.2f} rating!\n"
            response += f"   🎯 Try watching both to decide!"

        return response

    # ===== MOVIE GUESSING GAME =====
    def get_movie_guessing_game(self):
        """Movie guessing game"""
        games = [
            {
                "clue": "🎬 'I'll be back' - Which movie is this from?",
                "answer": "The Terminator",
                "hint": "A robot from the future",
                "year": 1984
            },
            {
                "clue": "🎬 'May the Force be with you' - Which movie is this from?",
                "answer": "Star Wars",
                "hint": "A long time ago in a galaxy far, far away...",
                "year": 1977
            },
            {
                "clue": "🎬 'You can't handle the truth!' - Which movie is this from?",
                "answer": "A Few Good Men",
                "hint": "A courtroom drama",
                "year": 1992
            },
            {
                "clue": "🎬 'Why so serious?' - Which movie is this from?",
                "answer": "The Dark Knight",
                "hint": "A superhero movie with a villain in makeup",
                "year": 2008
            },
            {
                "clue": "🎬 'Life is like a box of chocolates' - Which movie is this from?",
                "answer": "Forrest Gump",
                "hint": "A man with a low IQ who changes history",
                "year": 1994
            },
            {
                "clue": "🎬 'Houston, we have a problem' - Which movie is this from?",
                "answer": "Apollo 13",
                "hint": "A space mission gone wrong",
                "year": 1995
            },
            {
                "clue": "🎬 'There's no place like home' - Which movie is this from?",
                "answer": "The Wizard of Oz",
                "hint": "A girl in a magical land",
                "year": 1939
            },
            {
                "clue": "🎬 'I am your father' - Which movie is this from?",
                "answer": "Star Wars: The Empire Strikes Back",
                "hint": "A shocking family revelation",
                "year": 1980
            }
        ]

        # Randomly select a game
        game = random.choice(games)

        response = f"🎮 **Movie Guessing Game!**\n\n"
        response += f"{game['clue']}\n\n"
        response += f"💡 Hint: {game['hint']}\n"
        response += f"📅 Year: {game['year']}\n\n"
        response += f"🤔 Can you guess the movie? Type 'answer: [your guess]'"

        return response

    def check_movie_guess(self, query, game_answer):
        """Check if the user's guess is correct"""
        if "answer:" in query.lower():
            user_answer = query.lower().split("answer:")[1].strip()
            if user_answer in game_answer.lower():
                return f"🎉 **Correct!** The movie is **{game_answer}**! You're a movie expert! 🌟"
            else:
                return f"❌ **Not quite!** The correct answer is **{game_answer}**. Try again next time! 🎬"
        return None

    # ===== WEEKLY MOVIE SUGGESTION =====
    def get_weekly_suggestion(self):
        """Get weekly movie suggestion"""
        weekly_movies = [
            {"movie": "Inception", "reason": "A mind-bending thriller perfect for deep thinking"},
            {"movie": "The Godfather", "reason": "A classic masterpiece about family and power"},
            {"movie": "The Dark Knight", "reason": "An epic superhero film with incredible performances"},
            {"movie": "Pulp Fiction", "reason": "A groundbreaking film with unforgettable dialogue"},
            {"movie": "Forrest Gump", "reason": "A heartwarming story about life and love"},
            {"movie": "The Matrix", "reason": "A revolutionary sci-fi film that changed cinema"},
            {"movie": "The Shawshank Redemption", "reason": "A powerful story about hope and friendship"},
            {"movie": "Fight Club", "reason": "A mind-blowing film with an iconic twist"},
            {"movie": "Goodfellas", "reason": "The ultimate gangster film"},
            {"movie": "The Lion King", "reason": "A timeless animated masterpiece"}
        ]

        # Get day of week
        today = datetime.now().strftime("%A")
        week_num = datetime.now().isocalendar()[1]

        # Select movie based on week
        selected = weekly_movies[week_num % len(weekly_movies)]

        response = f"📅 **Weekly Movie Suggestion**\n"
        response += "=" * 40 + "\n\n"
        response += f"🎬 **Movie:** {selected['movie']}\n"
        response += f"💭 **Why watch:** {selected['reason']}\n\n"
        response += f"🌟 **Perfect for this {today}!** Enjoy watching! 🍿"

        return response

    # ===== FUN MOVIE QUIZZES =====
    def get_movie_quiz(self):
        """Get a movie quiz"""
        quizzes = [
            {
                "question": "Which actor played 'Jack Dawson' in Titanic?",
                "options": ["A) Brad Pitt", "B) Leonardo DiCaprio", "C) Tom Cruise", "D) Johnny Depp"],
                "answer": "B"
            },
            {
                "question": "What year was the first Star Wars movie released?",
                "options": ["A) 1977", "B) 1980", "C) 1983", "D) 1999"],
                "answer": "A"
            },
            {
                "question": "Which movie features the song 'My Heart Will Go On'?",
                "options": ["A) The Bodyguard", "B) Titanic", "C) Ghost", "D) Pretty Woman"],
                "answer": "B"
            },
            {
                "question": "What is the highest-grossing movie of all time (unadjusted for inflation)?",
                "options": ["A) Avatar", "B) Titanic", "C) Avengers: Endgame", "D) Star Wars"],
                "answer": "A"
            },
            {
                "question": "Which director made 'Pulp Fiction'?",
                "options": ["A) Steven Spielberg", "B) Martin Scorsese", "C) Quentin Tarantino",
                            "D) Christopher Nolan"],
                "answer": "C"
            },
            {
                "question": "Which movie is about a boy wizard?",
                "options": ["A) The Lord of the Rings", "B) Harry Potter", "C) Narnia", "D) Percy Jackson"],
                "answer": "B"
            }
        ]

        quiz = random.choice(quizzes)

        response = f"🧠 **Movie Quiz Time!**\n\n"
        response += f"❓ {quiz['question']}\n\n"
        response += f"{quiz['options'][0]}\n"
        response += f"{quiz['options'][1]}\n"
        response += f"{quiz['options'][2]}\n"
        response += f"{quiz['options'][3]}\n\n"
        response += f"💡 Type 'answer: A', 'answer: B', 'answer: C', or 'answer: D' to check!"

        return response

    def check_quiz_answer(self, query, quiz_answer):
        """Check if the quiz answer is correct"""
        if "answer:" in query.lower():
            user_answer = query.lower().split("answer:")[1].strip().upper()
            if user_answer == quiz_answer:
                return "🎉 **Correct!** You're a movie genius! 🌟"
            else:
                return f"❌ **Wrong!** The correct answer is **{quiz_answer}**. Keep learning! 📚"
        return None

    # ===== MOVIE TRIVIA CHALLENGE =====
    def get_trivia_challenge(self):
        """Get a movie trivia challenge with multiple facts"""
        trivia_facts = random.sample(self.movie_trivia, 3)

        response = f"🎯 **Movie Trivia Challenge!**\n\n"
        response += "Test your movie knowledge!\n\n"

        for i, fact in enumerate(trivia_facts, 1):
            response += f"{i}. {fact}\n"

        response += f"\n💡 **Challenge:** Can you guess which one is FALSE?"
        response += f"\nHint: All of them are TRUE! 😄"

        return response

    # ===== MOVIE RECOMMENDATION ENGINE FOR SPECIFIC OCCASIONS =====
    def get_occasion_recommendation(self, occasion):
        """Recommend movies for specific occasions"""
        occasion_movies = {
            "date": [
                {"movie": "The Notebook", "reason": "Romantic and emotional 💕"},
                {"movie": "Crazy Rich Asians", "reason": "Fun and romantic 💑"},
                {"movie": "La La Land", "reason": "Beautiful music and romance 🎵"},
                {"movie": "The Proposal", "reason": "Funny and romantic 😄"},
            ],
            "rainy": [
                {"movie": "The Shawshank Redemption", "reason": "Perfect for cozy watching ☕"},
                {"movie": "The Godfather", "reason": "A classic for any weather 🍿"},
                {"movie": "Pulp Fiction", "reason": "Quentin Tarantino at his best 🎬"},
                {"movie": "Good Will Hunting", "reason": "Heartwarming and inspiring 💫"},
            ],
            "weekend": [
                {"movie": "Avengers: Endgame", "reason": "Action-packed and thrilling ⚡"},
                {"movie": "The Dark Knight", "reason": "Epic superhero film 🦇"},
                {"movie": "Inception", "reason": "Mind-blowing and exciting 🧠"},
                {"movie": "The Matrix", "reason": "Revolutionary sci-fi 🤖"},
            ],
            "family": [
                {"movie": "The Lion King", "reason": "Perfect for the whole family 🦁"},
                {"movie": "Toy Story", "reason": "Fun for everyone 🎮"},
                {"movie": "Finding Nemo", "reason": "Heartwarming family adventure 🐠"},
                {"movie": "The Incredibles", "reason": "Superhero fun for all ages 🦸"},
            ],
            "action": [
                {"movie": "Mad Max: Fury Road", "reason": "Intense action and excitement 🚗"},
                {"movie": "John Wick", "reason": "Amazing fight scenes 🔫"},
                {"movie": "The Bourne Identity", "reason": "Spy thriller at its best 🕵️"},
                {"movie": "Die Hard", "reason": "Classic action movie 🎄"},
            ],
            "comedy": [
                {"movie": "The Hangover", "reason": "Hilarious and unforgettable 😂"},
                {"movie": "Superbad", "reason": "Teen comedy gold 🤣"},
                {"movie": "Bridesmaids", "reason": "Funny and heartwarming 💐"},
                {"movie": "Step Brothers", "reason": "Pure comedy madness 😄"},
            ]
        }

        movies = occasion_movies.get(occasion, occasion_movies["weekend"])
        selected = random.choice(movies)

        response = f"🎬 **Perfect for {occasion.title()}!**\n\n"
        response += f"📽️ **Movie:** {selected['movie']}\n"
        response += f"💭 **Why:** {selected['reason']}\n\n"
        response += "🎯 **Enjoy your movie!** 🍿"

        return response

    # ===== HANDLE GAME AND FUN RESPONSES =====
    def get_fun_response(self, query):
        """Get fun and entertaining responses - ENHANCED"""
        query_lower = query.lower()

        # 🎮 Movie Guessing Game
        if any(word in query_lower for word in ['guess the movie', 'movie game', 'guessing game', 'guess movie']):
            return self.get_movie_guessing_game()

        # 🧠 Movie Quiz
        if any(word in query_lower for word in ['quiz', 'movie quiz', 'film quiz', 'test my knowledge']):
            return self.get_movie_quiz()

        # 📅 Weekly suggestion
        if any(word in query_lower for word in
               ['weekly suggestion', 'suggest for this week', 'week movie', 'what to watch this week']):
            return self.get_weekly_suggestion()

        # 🎯 Trivia Challenge
        if any(word in query_lower for word in
               ['trivia challenge', 'movie trivia challenge', 'test my movie knowledge']):
            return self.get_trivia_challenge()

        # 💑 Date night recommendation
        if any(word in query_lower for word in ['date night', 'romantic movie', 'movie for date']):
            return self.get_occasion_recommendation("date")

        # ☕ Rainy day recommendation
        if any(word in query_lower for word in ['rainy day', 'movie for rain', 'cozy movie']):
            return self.get_occasion_recommendation("rainy")

        # 🎉 Weekend recommendation
        if any(word in query_lower for word in ['weekend movie', 'weekend watch', 'movie for weekend']):
            return self.get_occasion_recommendation("weekend")

        # 👨‍👩‍👧‍👦 Family night recommendation
        if any(word in query_lower for word in ['family movie', 'family night', 'kids movie']):
            return self.get_occasion_recommendation("family")

        # 💥 Action movie recommendation
        if any(word in query_lower for word in ['action movie', 'want action', 'action packed']):
            return self.get_occasion_recommendation("action")

        # 😂 Comedy movie recommendation
        if any(word in query_lower for word in ['comedy movie', 'funny movie', 'make me laugh']):
            return self.get_occasion_recommendation("comedy")

        # 💡 Trivia
        if any(word in query_lower for word in ['trivia', 'fact', 'did you know', 'interesting']):
            return f"💡 **Movie Fact:**\n{random.choice(self.movie_trivia)}"

        # 🎬 Quotes
        if any(word in query_lower for word in ['quote', 'dialogue', 'line', 'famous words']):
            return f"🎬 **Famous Movie Quote:**\n{random.choice(self.movie_quotes)}"

        # 😂 Jokes
        if any(word in query_lower for word in ['joke', 'funny', 'humor', 'laugh']):
            return f"😂 **Movie Joke:**\n{random.choice(self.movie_jokes)}"

        # 🎲 Random Movie
        if any(word in query_lower for word in ['random movie', 'surprise me', 'anything', "don't care"]):
            if self.data_loader:
                movie_id = random.choice(self.data_loader.movies['movie_id'].tolist())
                info = self.data_loader.get_movie_info(movie_id)
                if info:
                    return f"🎲 **Surprise Movie!**\n\n" \
                           f"🎬 {info['title']}\n" \
                           f"🎭 {', '.join(info['genres'])}\n" \
                           f"⭐ {info['avg_rating']:.2f}/5\n" \
                           f"📅 {info['year'] if info['year'] else 'N/A'}"

        # 📊 Compare (existing)
        if 'compare' in query_lower and 'and' in query_lower:
            return self.handle_compare(query)

        return None

    # ===== CONVERSATION HISTORY MANAGEMENT =====
    def save_conversation_history(self, filename="conversation_history.json"):
        """Save conversation history to file"""
        try:
            data = {
                "session_id": self.session_id,
                "conversations": self.conversation_history,
                "total_messages": len(self.conversation_history),
                "user_preferences": self.user_preferences
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return f"✅ Conversation history saved to {filename}"
        except Exception as e:
            return f"❌ Error saving history: {str(e)}"

    def load_conversation_history(self, filename="conversation_history.json"):
        """Load conversation history from file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.conversation_history = data.get("conversations", [])
            self.user_preferences = data.get("user_preferences", {})
            return f"✅ Loaded {len(self.conversation_history)} conversations"
        except FileNotFoundError:
            return "ℹ️ No saved conversation history found"
        except Exception as e:
            return f"❌ Error loading history: {str(e)}"

    def get_conversation_summary(self):
        """Get summary of conversation history"""
        if not self.conversation_history:
            return "📊 No conversations yet!"

        total = len(self.conversation_history)
        topics = defaultdict(int)
        timestamps = []

        for conv in self.conversation_history:
            text = conv.get("user", "")
            timestamps.append(conv.get("timestamp", datetime.now()))

            # Detect topics
            if any(word in text.lower() for word in ['action', 'adventure', 'comedy', 'drama']):
                topics["genre"] += 1
            if any(word in text.lower() for word in ['year', '2000', '1995', '2010']):
                topics["year"] += 1
            if any(word in text.lower() for word in ['rating', 'star', 'score']):
                topics["rating"] += 1
            if any(word in text.lower() for word in ['recommend', 'suggest', 'find']):
                topics["recommendation"] += 1
            if any(word in text.lower() for word in ['game', 'quiz', 'trivia']):
                topics["game"] += 1

        first = min(timestamps) if timestamps else datetime.now()
        last = max(timestamps) if timestamps else datetime.now()

        response = f"📊 **Conversation Summary**\n"
        response += "=" * 40 + "\n\n"
        response += f"💬 Total Messages: {total}\n"
        response += f"📅 Started: {first.strftime('%A, %B %d, %Y')}\n"
        response += f"⏰ Last Activity: {last.strftime('%H:%M')}\n\n"
        response += f"🎯 **Topics Discussed:**\n"

        for topic, count in topics.items():
            if count > 0:
                response += f"   • {topic.title()}: {count} times\n"

        if self.user_preferences:
            response += f"\n📌 **Your Preferences:**\n"
            for key, value in self.user_preferences.items():
                response += f"   • {key}: {value}\n"

        return response

    def get_follow_up_question(self, previous_query):
        """Generate a follow-up question based on previous query"""
        previous_lower = previous_query.lower()

        if 'genre' in previous_lower or 'action' in previous_lower or 'comedy' in previous_lower:
            return "What genre would you like to watch? 🎭 (Action, Comedy, Drama, etc.)"
        elif 'year' in previous_lower or '2024' in previous_lower or '2000' in previous_lower:
            return "What year range are you interested in? 📅"
        elif 'rating' in previous_lower or 'star' in previous_lower:
            return "What minimum rating would you like? ⭐ (1-5)"
        elif 'movie' in previous_lower or 'film' in previous_lower:
            return "Would you like me to recommend some movies? 🎬"
        else:
            return "What kind of movie are you looking for? 🎥"

    def process_follow_up(self, query):
        """Process follow-up questions"""
        query_lower = query.lower()

        if any(word in query_lower for word in ['yes', 'sure', 'ok', 'please', 'yeah']):
            return "🎬 Let me find some great movie recommendations for you!"
        elif any(word in query_lower for word in ['no', 'not', 'maybe', 'don\'t', 'dont']):
            return "🤔 What would you like to know about movies then?"
        else:
            return self.get_follow_up_question(query)

    # ===== USER PREFERENCE MANAGEMENT =====
    def update_user_preferences(self, query):
        """Update user preferences based on conversation"""
        query_lower = query.lower()

        # Detect genre preference
        genres = self.data_loader.get_all_genres() if self.data_loader else []
        for genre in genres:
            if genre.lower() in query_lower:
                self.user_preferences["favorite_genre"] = genre

        # Detect rating preference
        rating = self.extract_rating(query_lower)
        if rating:
            self.user_preferences["preferred_rating"] = rating

        # Detect year preference
        year = self.extract_year(query_lower)
        if year:
            self.user_preferences["preferred_year"] = year

        # Count queries
        if "recommend" in query_lower or "suggest" in query_lower:
            self.user_preferences["recommendation_requests"] = self.user_preferences.get("recommendation_requests",
                                                                                         0) + 1

        return self.user_preferences

    def get_user_profile(self):
        """Get user profile summary"""
        if not self.user_preferences:
            return "👤 No preferences saved yet! Start chatting to build your profile."

        response = f"👤 **User Profile**\n"
        response += "=" * 40 + "\n\n"

        for key, value in self.user_preferences.items():
            if key == "favorite_genre":
                response += f"🎭 Favorite Genre: {value}\n"
            elif key == "preferred_rating":
                response += f"⭐ Preferred Rating: {value}+ stars\n"
            elif key == "preferred_year":
                response += f"📅 Preferred Year: {value}\n"
            elif key == "recommendation_requests":
                response += f"📊 Recommendations Requested: {value} times\n"
            else:
                response += f"📌 {key}: {value}\n"

        return response

    # ===== ENHANCED PROCESS_QUERY WITH DIALOGUE =====
    def process_query(self, query):
        """Main query processing with enhanced dialogue"""
        query_lower = query.lower().strip()

        # ===== CONVERSATION HISTORY =====
        self.conversation_count += 1
        self.conversation_history.append({
            "user": query,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # ===== MOOD DETECTION =====
        self.user_mood = self.detect_user_mood(query_lower)

        # ===== UPDATE USER PREFERENCES =====
        self.update_user_preferences(query)

        # ===== CHECK FOR SAVE HISTORY =====
        if any(word in query_lower for word in ['save history', 'save conversation', 'save chat']):
            return self.save_conversation_history()

        # ===== CHECK FOR LOAD HISTORY =====
        if any(word in query_lower for word in ['load history', 'load conversation', 'load chat']):
            return self.load_conversation_history()

        # ===== CHECK FOR CONVERSATION SUMMARY =====
        if any(word in query_lower for word in
               ['history', 'conversation summary', 'chat summary', 'what did we talk about']):
            return self.get_conversation_summary()

        # ===== CHECK FOR USER PROFILE =====
        if any(word in query_lower for word in ['profile', 'my preferences', 'my info', 'user preferences']):
            return self.get_user_profile()

        # ===== CHECK FOR FOLLOW-UP =====
        if self.last_topic and any(word in query_lower for word in ['yes', 'no', 'maybe', 'ok', 'sure', 'not']):
            response = self.process_follow_up(query)
            self.last_topic = None
            return response

        # ===== FUN RESPONSES (Step 2) =====
        fun_response = self.get_fun_response(query)
        if fun_response:
            self.last_topic = "fun"
            return fun_response

        # ===== HELP =====
        if any(word in query_lower for word in ['help', 'what can you do', 'capabilities', 'guide']):
            return self.get_help_response()

        # ===== GREETINGS =====
        if any(g in query_lower for g in
               ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']):
            response = random.choice(self.greetings)
            self.last_topic = "greeting"
            return response

        # ===== FAREWELL =====
        if any(f in query_lower for f in ['bye', 'goodbye', 'see you', 'later', 'cya', 'take care']):
            response = random.choice(self.farewells)
            self.last_topic = "farewell"
            return response

        # ===== DATE/TIME =====
        if any(d in query_lower for d in ['date', 'today', 'time', 'what day', 'what is the date']):
            now = datetime.now()
            return f"📅 Today is {now.strftime('%A, %B %d, %Y')}\n⏰ Time: {now.strftime('%H:%M:%S')}\n🎬 Perfect time for a movie!"

        # ===== MOOD RECOMMENDATIONS =====
        if any(word in query_lower for word in
               ['mood', 'feel', 'emotion', 'feeling', 'happy', 'sad', 'bored', 'excited', 'romantic', 'curious',
                'relaxed', 'thoughtful']):
            return self.get_mood_recommendations()

        # ===== GENRE LIST =====
        if any(g in query_lower for g in ['genres', 'list genres', 'show genres', 'categories']):
            if self.data_loader:
                genres = self.data_loader.get_all_genres()
                self.last_topic = "genres"
                return f"🎭 **Available Genres:**\n" + "• " + "\n• ".join(genres)
            return "Please load the dataset first!"

        # ===== RECOMMENDATIONS =====
        if any(r in query_lower for r in ['recommend', 'suggest', 'find', 'show me', 'looking for', 'want to watch']):
            if not self.data_loader:
                return "Please load the dataset first!"

            genre = self.extract_genre(query_lower)
            year = self.extract_year(query_lower)
            rating = self.extract_rating(query_lower)
            count = self.extract_count(query_lower)

            recs = self.data_loader.get_popular_movies(
                n=count,
                genre=genre,
                year=year,
                min_rating=rating if rating else 0
            )

            if not recs:
                follow_up = f"No movies found with your criteria!\n{self.get_follow_up_question(query)}"
                self.last_topic = "no_results"
                return follow_up

            response = f"🎬 **Found {len(recs)} movies for you:**\n\n"
            for i, movie in enumerate(recs[:count], 1):
                response += f"{i}. {movie['title'][:50]}\n"
                response += f"   🎭 {', '.join(movie['genres'][:3])}\n"
                response += f"   📅 {movie.get('year', 'N/A')} | ⭐ {movie['avg_rating']:.1f}/5\n\n"

            filter_desc = []
            if genre: filter_desc.append(f"Genre: {genre}")
            if year: filter_desc.append(f"Year: {year}")
            if rating: filter_desc.append(f"Min Rating: {rating}")

            if filter_desc:
                response += f"💡 **Why this result?** I found these movies based on: {', '.join(filter_desc)}\n"

            response += f"\n❓ {self.get_follow_up_question(query)}"
            self.last_topic = "recommendation"
            return response

        # ===== MOVIE INFO =====
        if any(i in query_lower for i in ['about', 'info', 'details', 'tell me about', 'movie called']):
            if not self.data_loader:
                return "Please load the dataset first!"

            movie_title = self.extract_movie_title(query_lower)

            if not movie_title:
                return "Please specify a movie title! 🎬\nExample: 'Tell me about The Matrix'"

            movies = self.data_loader.movies
            found = movies[movies['title'].str.contains(movie_title, case=False, na=False)]

            if len(found) == 0:
                return f"Movie '{movie_title}' not found! Try another title."

            if len(found) > 1:
                titles = [f"{i + 1}. {row['title']}" for i, row in found.head(5).iterrows()]
                self.last_topic = "movie_found"
                return f"Found multiple movies:\n" + "\n".join(titles)

            movie_id = found.iloc[0]['movie_id']
            info = self.data_loader.get_movie_info(movie_id)

            if not info:
                return "Movie details not available!"

            response = f"🎬 **{info['title']}**\n"
            response += "=" * 40 + "\n"
            response += f"📅 Year: {info['year'] if info['year'] else 'N/A'}\n"
            response += f"🎭 Genres: {', '.join(info['genres'])}\n"
            response += f"⭐ Rating: {info['avg_rating']:.2f}/5\n"

            ratings = self.data_loader.get_movie_ratings(movie_id)
            response += f"📊 Votes: {len(ratings)}\n"

            response += f"\n💡 **Movie Fact:** {random.choice(self.movie_trivia)}"

            self.last_topic = "movie_info"
            return response

        # ===== POPULAR MOVIES =====
        if any(p in query_lower for p in ['popular', 'top', 'best', 'highest rated', 'trending']):
            if not self.data_loader:
                return "Please load the dataset first!"

            count = self.extract_count(query_lower)
            genre = self.extract_genre(query_lower)

            popular = self.data_loader.get_popular_movies(n=count, genre=genre)

            if not popular:
                return "No popular movies found!"

            response = f"🔥 **Top {len(popular)} Popular Movies:**\n\n"
            for i, movie in enumerate(popular[:count], 1):
                response += f"{i}. {movie['title'][:50]}\n"
                response += f"   ⭐ {movie['avg_rating']:.1f} | 🎭 {', '.join(movie['genres'][:3])}\n"
                response += f"   📊 {movie['num_ratings']} votes\n\n"

            self.last_topic = "popular"
            return response

        # ===== SAVE PREFERENCES =====
        if any(word in query_lower for word in ['save preference', 'remember this', 'favorite']):
            self.user_preferences["favorite_genre"] = self.extract_genre(query_lower) or "unknown"
            self.user_preferences["preferred_year"] = self.extract_year(query_lower) or "unknown"
            return "✅ **Preferences saved!** I'll remember what you like! 🎬"

        # ===== DEFAULT =====
        response = random.choice(self.unknown_responses)
        self.last_topic = "unknown"
        return response

    # ===== TMDB API INTEGRATION =====
    def get_tmdb_movie_details(self, movie_title):
        """Get movie details from TMDB API"""
        try:
            import requests
            # TMDB API key (you need to get your own)
            api_key = "YOUR_TMDB_API_KEY"  # Register at https://www.themoviedb.org/

            # Search for movie
            search_url = f"https://api.themoviedb.org/3/search/movie"
            params = {
                "api_key": api_key,
                "query": movie_title,
                "language": "en-US"
            }

            response = requests.get(search_url, params=params)
            data = response.json()

            if data.get("results") and len(data["results"]) > 0:
                movie = data["results"][0]
                movie_id = movie["id"]

                # Get detailed info
                details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
                detail_params = {
                    "api_key": api_key,
                    "language": "en-US",
                    "append_to_response": "credits,images,videos"
                }

                details = requests.get(details_url, params=detail_params)
                details_data = details.json()

                return self.format_tmdb_response(details_data)

            return None
        except Exception as e:
            return f"❌ Error connecting to TMDB: {str(e)}"

    def format_tmdb_response(self, movie_data):
        """Format TMDB response"""
        response = f"🎬 **{movie_data.get('title', 'Unknown')}**\n"
        response += "=" * 50 + "\n\n"

        response += f"📅 Release Date: {movie_data.get('release_date', 'N/A')}\n"
        response += f"⭐ TMDB Rating: {movie_data.get('vote_average', 0):.1f}/10\n"
        response += f"📊 Votes: {movie_data.get('vote_count', 0)}\n"
        response += f"⏱️ Runtime: {movie_data.get('runtime', 'N/A')} minutes\n"

        if movie_data.get('genres'):
            genres = ', '.join([g['name'] for g in movie_data['genres'][:3]])
            response += f"🎭 Genres: {genres}\n"

        if movie_data.get('overview'):
            response += f"\n📝 **Plot:**\n{movie_data['overview'][:300]}...\n"

        if movie_data.get('credits'):
            crew = movie_data['credits'].get('crew', [])
            director = next((p for p in crew if p['job'] == 'Director'), None)
            if director:
                response += f"\n🎥 Director: {director['name']}\n"

            cast = movie_data['credits'].get('cast', [])[:3]
            if cast:
                response += f"\n⭐ **Top Cast:**\n"
                for actor in cast:
                    response += f"   • {actor['name']} as {actor['character']}\n"

        if movie_data.get('images') and movie_data['images'].get('posters'):
            poster = movie_data['images']['posters'][0]['file_path']
            response += f"\n🖼️ Poster URL: https://image.tmdb.org/t/p/w500{poster}\n"

        return response

    # ===== OMDB API INTEGRATION =====
    def get_omdb_movie_details(self, movie_title):
        """Get movie details from OMDB API"""
        try:
            import requests
            # OMDB API key (you need to get your own)
            api_key = "YOUR_OMDB_API_KEY"  # Register at http://www.omdbapi.com/

            url = "http://www.omdbapi.com/"
            params = {
                "apikey": api_key,
                "t": movie_title,
                "plot": "full"
            }

            response = requests.get(url, params=params)
            data = response.json()

            if data.get("Response") == "True":
                return self.format_omdb_response(data)
            return None
        except Exception as e:
            return f"❌ Error connecting to OMDB: {str(e)}"

    def format_omdb_response(self, data):
        """Format OMDB response"""
        response = f"🎬 **{data.get('Title', 'Unknown')}**\n"
        response += "=" * 50 + "\n\n"

        response += f"📅 Year: {data.get('Year', 'N/A')}\n"
        response += f"⭐ IMDB Rating: {data.get('imdbRating', 'N/A')}/10\n"
        response += f"📊 IMDB Votes: {data.get('imdbVotes', 'N/A')}\n"
        response += f"⏱️ Runtime: {data.get('Runtime', 'N/A')}\n"
        response += f"🎭 Genres: {data.get('Genre', 'N/A')}\n"
        response += f"🎥 Director: {data.get('Director', 'N/A')}\n"
        response += f"⭐ Cast: {data.get('Actors', 'N/A')}\n"

        if data.get('Plot'):
            response += f"\n📝 **Plot:**\n{data.get('Plot', 'N/A')}\n"

        if data.get('Awards') and data['Awards'] != 'N/A':
            response += f"\n🏆 Awards: {data['Awards']}\n"

        if data.get('Poster') and data['Poster'] != 'N/A':
            response += f"\n🖼️ Poster: {data['Poster']}\n"

        return response

    # ===== YOUTUBE TRAILER =====
    def get_youtube_trailer(self, movie_title):
        """Get YouTube trailer for a movie"""
        try:
            import requests
            # YouTube API key (you need to get your own)
            api_key = "YOUR_YOUTUBE_API_KEY"

            search_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": f"{movie_title} trailer",
                "type": "video",
                "key": api_key,
                "maxResults": 1
            }

            response = requests.get(search_url, params=params)
            data = response.json()

            if data.get("items") and len(data["items"]) > 0:
                video_id = data["items"][0]["id"]["videoId"]
                return f"🎥 **Watch Trailer:**\nhttps://www.youtube.com/watch?v={video_id}"
            return None
        except Exception as e:
            return f"❌ Error connecting to YouTube: {str(e)}"

    # ===== CHECK MOVIE AVAILABILITY =====
    def check_movie_availability(self, movie_title):
        """Check if a movie is available on streaming platforms"""
        # This would require integration with streaming API services
        response = f"🔍 **Checking availability for '{movie_title}'**\n"
        response += "=" * 40 + "\n\n"

        # Mock availability (you can integrate with real streaming APIs)
        platforms = [
            "Netflix", "Amazon Prime", "Disney+", "HBO Max", "Apple TV+"
        ]

        available = random.sample(platforms, random.randint(1, 3))
        not_available = [p for p in platforms if p not in available]

        if available:
            response += "✅ **Available on:**\n"
            for platform in available:
                response += f"   • {platform}\n"

        if not_available:
            response += "\n❌ **Not available on:**\n"
            for platform in not_available:
                response += f"   • {platform}\n"

        response += "\n💡 Check local streaming services for more options!"

        return response

    # ===== ENHANCE PROCESS_QUERY WITH API INTEGRATION =====
    def process_query(self, query):
        """Main query processing with API integration"""
        query_lower = query.lower().strip()

        # ... (existing code from earlier steps remains)

        # ===== CHECK FOR TMDB API =====
        if any(word in query_lower for word in ['tmdb', 'the movie database']):
            movie_title = self.extract_movie_title(query_lower)
            if movie_title:
                return self.get_tmdb_movie_details(movie_title)
            return "Which movie do you want to search on TMDB? 🎬"

        # ===== CHECK FOR OMDB API =====
        if any(word in query_lower for word in ['omdb', 'imdb']):
            movie_title = self.extract_movie_title(query_lower)
            if movie_title:
                return self.get_omdb_movie_details(movie_title)
            return "Which movie do you want to search on OMDB? 🎬"

        # ===== CHECK FOR YOUTUBE TRAILER =====
        if any(word in query_lower for word in ['trailer', 'watch trailer', 'youtube trailer']):
            movie_title = self.extract_movie_title(query_lower)
            if movie_title:
                result = self.get_youtube_trailer(movie_title)
                if result:
                    return result
                return f"❌ Could not find trailer for '{movie_title}'"
            return "Which movie trailer do you want to watch? 🎬"

        # ===== CHECK FOR AVAILABILITY =====
        if any(word in query_lower for word in ['available', 'streaming', 'where to watch', 'watch']):
            movie_title = self.extract_movie_title(query_lower)
            if movie_title:
                return self.check_movie_availability(movie_title)
            return "Which movie do you want to check availability for? 🎬"

        # ===== ... rest of existing code remains ... =====
    def process_query(self, query):
        """Main query processing"""
        query_lower = query.lower().strip()

        # Conversation history
        self.conversation_count += 1
        self.conversation_history.append({"user": query, "timestamp": datetime.now()})

        # Mood detection
        self.user_mood = self.detect_user_mood(query_lower)

        # Fun responses
        fun_response = self.get_fun_response(query)
        if fun_response:
            return fun_response

        # Help
        if any(word in query_lower for word in ['help', 'what can you do', 'capabilities', 'guide']):
            return self.get_help_response()

        # Greetings
        if any(g in query_lower for g in
               ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']):
            return random.choice(self.greetings)

        # Farewell
        if any(f in query_lower for f in ['bye', 'goodbye', 'see you', 'later', 'cya', 'take care']):
            return random.choice(self.farewells)

        # Date/Time
        if any(d in query_lower for d in ['date', 'today', 'time', 'what day', 'what is the date']):
            now = datetime.now()
            return f"📅 Today is {now.strftime('%A, %B %d, %Y')}\n⏰ Time: {now.strftime('%H:%M:%S')}\n🎬 Perfect time for a movie!"

        # Mood-based recommendations
        if any(word in query_lower for word in
               ['mood', 'feel', 'emotion', 'feeling', 'happy', 'sad', 'bored', 'excited', 'romantic', 'curious',
                'relaxed', 'thoughtful']):
            return self.get_mood_recommendations()

        # Genre list
        if any(g in query_lower for g in ['genres', 'list genres', 'show genres', 'categories']):
            if self.data_loader:
                genres = self.data_loader.get_all_genres()
                return f"🎭 **Available Genres:**\n" + "• " + "\n• ".join(genres)
            return "Please load the dataset first!"

        # Recommendations
        if any(r in query_lower for r in ['recommend', 'suggest', 'find', 'show me', 'looking for', 'want to watch']):
            if not self.data_loader:
                return "Please load the dataset first!"

            genre = self.extract_genre(query_lower)
            year = self.extract_year(query_lower)
            rating = self.extract_rating(query_lower)
            count = self.extract_count(query_lower)

            recs = self.data_loader.get_popular_movies(
                n=count,
                genre=genre,
                year=year,
                min_rating=rating if rating else 0
            )

            if not recs:
                return "No movies found with your criteria! Try different filters."

            response = f"🎬 **Found {len(recs)} movies for you:**\n\n"
            for i, movie in enumerate(recs[:count], 1):
                response += f"{i}. {movie['title'][:50]}\n"
                response += f"   🎭 {', '.join(movie['genres'][:3])}\n"
                response += f"   📅 {movie.get('year', 'N/A')} | ⭐ {movie['avg_rating']:.1f}/5\n\n"

            filter_desc = []
            if genre: filter_desc.append(f"Genre: {genre}")
            if year: filter_desc.append(f"Year: {year}")
            if rating: filter_desc.append(f"Min Rating: {rating}")

            if filter_desc:
                response += f"💡 **Why this result?** I found these movies based on: {', '.join(filter_desc)}"

            return response

        # Movie info
        if any(i in query_lower for i in ['about', 'info', 'details', 'tell me about', 'movie called']):
            if not self.data_loader:
                return "Please load the dataset first!"

            movie_title = self.extract_movie_title(query_lower)

            if not movie_title:
                return "Please specify a movie title! 🎬\nExample: 'Tell me about The Matrix'"

            movies = self.data_loader.movies
            found = movies[movies['title'].str.contains(movie_title, case=False, na=False)]

            if len(found) == 0:
                return f"Movie '{movie_title}' not found! Try another title."

            if len(found) > 1:
                titles = [f"{i + 1}. {row['title']}" for i, row in found.head(5).iterrows()]
                return f"Found multiple movies:\n" + "\n".join(titles)

            movie_id = found.iloc[0]['movie_id']
            info = self.data_loader.get_movie_info(movie_id)

            if not info:
                return "Movie details not available!"

            response = f"🎬 **{info['title']}**\n"
            response += "=" * 40 + "\n"
            response += f"📅 Year: {info['year'] if info['year'] else 'N/A'}\n"
            response += f"🎭 Genres: {', '.join(info['genres'])}\n"
            response += f"⭐ Rating: {info['avg_rating']:.2f}/5\n"

            ratings = self.data_loader.get_movie_ratings(movie_id)
            response += f"📊 Votes: {len(ratings)}\n"

            response += f"\n💡 **Movie Fact:** {random.choice(self.movie_trivia)}"

            return response

        # Random movie
        if any(r in query_lower for r in ['random', 'surprise me', 'anything', "don't care"]):
            if not self.data_loader:
                return "Please load the dataset first!"

            movie_id = random.choice(self.data_loader.movies['movie_id'].tolist())
            info = self.data_loader.get_movie_info(movie_id)

            if not info:
                return "Could not find a random movie!"

            return f"🎲 **Surprise Movie!**\n\n" \
                   f"🎬 {info['title']}\n" \
                   f"🎭 {', '.join(info['genres'])}\n" \
                   f"⭐ {info['avg_rating']:.2f}/5\n" \
                   f"📅 {info['year'] if info['year'] else 'N/A'}"

        # Popular movies
        if any(p in query_lower for p in ['popular', 'top', 'best', 'highest rated', 'trending']):
            if not self.data_loader:
                return "Please load the dataset first!"

            count = self.extract_count(query_lower)
            genre = self.extract_genre(query_lower)

            popular = self.data_loader.get_popular_movies(n=count, genre=genre)

            if not popular:
                return "No popular movies found!"

            response = f"🔥 **Top {len(popular)} Popular Movies:**\n\n"
            for i, movie in enumerate(popular[:count], 1):
                response += f"{i}. {movie['title'][:50]}\n"
                response += f"   ⭐ {movie['avg_rating']:.1f} | 🎭 {', '.join(movie['genres'][:3])}\n"
                response += f"   📊 {movie['num_ratings']} votes\n\n"

            return response

        # Default
        return random.choice(self.unknown_responses)

    def extract_genre(self, text):
        if not self.data_loader:
            return None
        genres = self.data_loader.get_all_genres()
        for genre in genres:
            if genre.lower() in text.lower():
                return genre
        return None

    def extract_year(self, text):
        year_match = re.search(r'\b(19[0-9]{2}|20[0-9]{2})\b', text)
        if year_match:
            year = int(year_match.group())
            if 1900 <= year <= 2026:
                return year
        return None

    def extract_rating(self, text):
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

        if '10' in text or 'ten' in text: return 10
        if '5' in text or 'five' in text: return 5
        if '20' in text or 'twenty' in text: return 20
        if '30' in text or 'thirty' in text: return 30
        return 10

    def extract_movie_title(self, text):
        patterns = [
            r'about\s+([A-Za-z0-9\s]+?)(?:\s+\(|$|\.|\?)',
            r'info\s+([A-Za-z0-9\s]+?)(?:\s+\(|$|\.|\?)',
            r'movie\s+called\s+([A-Za-z0-9\s]+?)(?:\s+\(|$|\.|\?)',
            r'film\s+called\s+([A-Za-z0-9\s]+?)(?:\s+\(|$|\.|\?)',
            r'tell me about\s+([A-Za-z0-9\s]+?)(?:\s+\(|$|\.|\?)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        if self.data_loader:
            movies = self.data_loader.movies
            words = text.split()
            for word in words:
                if len(word) > 3:
                    found = movies[movies['title'].str.contains(word, case=False, na=False)]
                    if len(found) > 0:
                        return word
        return None