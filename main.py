import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import os
import sys
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import MovieDataLoader
from src.collaborative import CollaborativeFiltering
from src.content_based import ContentBasedRecommender
from src.hybrid import HybridRecommender
from chatbot import MovieChatbot
from chatbot_advanced import AdvancedMovieChatbot
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MovieChatbotApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("🎬 Movie Recommendation Chatbot")
        self.window.geometry("1300x800")
        self.window.resizable(True, True)

        # Data
        self.data_loader = None
        self.cf_model = None
        self.cb_model = None
        self.hybrid_model = None
        self.is_loaded = False
        self.movie_ids = {}

        # Chatbot
        self.chatbot = AdvancedMovieChatbot()

        # Setup UI
        self.setup_ui()

        # Load data
        self.load_data_thread()

    def setup_ui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # ========== LEFT PANEL - FILTERS ==========
        left_panel = ctk.CTkFrame(self.main_frame, width=280)
        left_panel.pack(side="left", fill="y", padx=(0, 15))
        left_panel.pack_propagate(False)

        # Title
        ctk.CTkLabel(
            left_panel,
            text="🎬 Movie Filter",
            font=("Arial", 20, "bold")
        ).pack(pady=(10, 15))

        # Genre
        ctk.CTkLabel(left_panel, text="🎭 Genre:", font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(5, 0))
        self.genre_var = ctk.StringVar(value="All")
        self.genre_menu = ctk.CTkOptionMenu(
            left_panel,
            values=["All"],
            variable=self.genre_var,
            width=240
        )
        self.genre_menu.pack(pady=5, padx=15)

        # Year - now with full range
        ctk.CTkLabel(left_panel, text="📅 Year:", font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.year_var = ctk.StringVar(value="All")
        self.year_menu = ctk.CTkOptionMenu(
            left_panel,
            values=["All"],
            variable=self.year_var,
            width=240
        )
        self.year_menu.pack(pady=5, padx=15)

        # Rating
        ctk.CTkLabel(left_panel, text="⭐ Min Rating:", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                        pady=(10, 0))
        self.rating_var = ctk.StringVar(value="0")
        self.rating_menu = ctk.CTkOptionMenu(
            left_panel,
            values=["0", "1", "2", "3", "4", "4.5"],
            variable=self.rating_var,
            width=240
        )
        self.rating_menu.pack(pady=5, padx=15)

        # Number
        ctk.CTkLabel(left_panel, text="📊 Count:", font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.count_var = ctk.StringVar(value="10")
        self.count_menu = ctk.CTkOptionMenu(
            left_panel,
            values=["5", "10", "15", "20", "30", "50"],
            variable=self.count_var,
            width=240
        )
        self.count_menu.pack(pady=5, padx=15)

        # Model
        ctk.CTkLabel(left_panel, text="🤖 Model:", font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.model_var = ctk.StringVar(value="Hybrid")
        self.model_menu = ctk.CTkOptionMenu(
            left_panel,
            values=["Collaborative", "Content-Based", "Hybrid"],
            variable=self.model_var,
            width=240
        )
        self.model_menu.pack(pady=5, padx=15)

        # Buttons
        ctk.CTkButton(
            left_panel,
            text="🤖 Train Models",
            command=self.train_models_thread,
            fg_color="#2C3E50",
            height=40
        ).pack(pady=10, padx=15, fill="x")

        ctk.CTkButton(
            left_panel,
            text="🎯 Show Recommendations",
            command=self.show_recommendations,
            fg_color="#27AE60",
            height=45,
            font=("Arial", 14, "bold")
        ).pack(pady=5, padx=15, fill="x")

        # Status
        self.status_label = ctk.CTkLabel(
            left_panel,
            text="⏳ Loading...",
            font=("Arial", 11)
        )
        self.status_label.pack(pady=(15, 5))

        self.progress_bar = ctk.CTkProgressBar(left_panel, width=240)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)

        # ========== MIDDLE PANEL - MOVIE LIST ==========
        middle_panel = ctk.CTkFrame(self.main_frame)
        middle_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))

        ctk.CTkLabel(
            middle_panel,
            text="📋 Movie List",
            font=("Arial", 18, "bold")
        ).pack(pady=(5, 10))

        list_frame = ctk.CTkFrame(middle_panel)
        list_frame.pack(fill="both", expand=True)

        self.movie_listbox = tk.Listbox(
            list_frame,
            bg="#2b2b2b",
            fg="#ffffff",
            selectbackground="#2E86AB",
            selectforeground="#ffffff",
            font=("Arial", 12),
            height=20
        )
        self.movie_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        self.movie_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.movie_listbox.yview)

        self.movie_listbox.bind('<<ListboxSelect>>', self.on_movie_select)

        # ========== RIGHT PANEL - CHATBOT ==========
        right_panel = ctk.CTkFrame(self.main_frame, width=350)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)

        ctk.CTkLabel(
            right_panel,
            text="🤖 Movie Chatbot",
            font=("Arial", 18, "bold")
        ).pack(pady=(5, 10))

        self.chat_display = ctk.CTkTextbox(
            right_panel,
            font=("Arial", 12),
            wrap="word",
            height=400
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.chat_display.insert("end", "🤖 Hello! I'm your Movie Assistant!\n\n")
        self.chat_display.insert("end", "I can help you with:\n")
        self.chat_display.insert("end", "• 🎭 Find movies by genre\n")
        self.chat_display.insert("end", "• 📅 Search by year\n")
        self.chat_display.insert("end", "• ⭐ Filter by rating\n")
        self.chat_display.insert("end", "• 📊 Get recommendations\n")
        self.chat_display.insert("end", "• 📖 Movie details\n")
        self.chat_display.insert("end", "• 🎲 Random movie suggestions\n\n")
        self.chat_display.insert("end", "Just type anything! 🎬\n")
        self.chat_display.insert("end", "=" * 40 + "\n\n")

        input_frame = ctk.CTkFrame(right_panel)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.chat_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ask about movies or just chat...",
            font=("Arial", 13)
        )
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            command=self.send_chat_message,
            width=70,
            fg_color="#2E86AB"
        )
        self.send_btn.pack(side="right")

        self.chat_input.bind("<Return>", lambda e: self.send_chat_message())

        info_frame = ctk.CTkFrame(right_panel)
        info_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            info_frame,
            text="📖 Movie Details",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(5, 5))

        self.movie_info_text = ctk.CTkTextbox(
            info_frame,
            font=("Arial", 12),
            height=120,
            wrap="word"
        )
        self.movie_info_text.pack(fill="x", pady=(0, 5))
        self.movie_info_text.insert("end", "Select a movie from the list to see details...")

    def load_data_thread(self):
        def load():
            try:
                self.status_label.configure(text="📥 Loading MovieLens...")
                self.progress_bar.set(0.2)

                self.data_loader = MovieDataLoader('data/ml-100k/')
                self.data_loader.load_all_data()

                self.progress_bar.set(0.5)
                self.status_label.configure(text="✅ Loaded! Preparing filters...")

                # Update genre
                genres = self.data_loader.get_all_genres()
                self.genre_menu.configure(values=["All"] + genres)

                # Update year - FULL RANGE from 1900 to 2026
                all_years = list(range(2026, 1899, -1))
                self.year_menu.configure(values=["All"] + [str(y) for y in all_years])

                # Set chatbot data loader
                self.chatbot.set_data_loader(self.data_loader)

                # Initialize models
                self.cf_model = CollaborativeFiltering(self.data_loader)
                self.cb_model = ContentBasedRecommender(self.data_loader)
                self.hybrid_model = HybridRecommender(self.data_loader)

                self.progress_bar.set(0.8)
                self.show_popular_movies()

                self.progress_bar.set(1.0)
                self.is_loaded = True
                self.status_label.configure(text="✅ Ready! Use filters or chat with me!")

                self.add_chat_message("system", "✅ Dataset loaded successfully!")
                self.add_chat_message("system", f"📊 {len(self.data_loader.movies)} movies available!")

            except Exception as e:
                self.status_label.configure(text=f"❌ Error: {str(e)}")
                messagebox.showerror("Error", f"Error loading dataset:\n{str(e)}")

        thread = threading.Thread(target=load)
        thread.daemon = True
        thread.start()

    def show_popular_movies(self):
        if not self.is_loaded:
            return

        popular = self.data_loader.get_popular_movies(20)
        self.movie_listbox.delete(0, tk.END)
        self.movie_ids = {}

        for idx, movie in enumerate(popular):
            display_text = f"⭐ {movie['title'][:50]} | {movie['avg_rating']:.1f} ★"
            self.movie_listbox.insert(tk.END, display_text)
            self.movie_ids[idx] = movie['movie_id']

    def show_recommendations(self):
        if not self.is_loaded:
            messagebox.showwarning("Error", "Dataset not loaded!")
            return

        try:
            n = int(self.count_var.get())
            genre = self.genre_var.get()
            if genre == "All":
                genre = None

            year = self.year_var.get()
            if year == "All":
                year = None
            else:
                year = int(year)

            min_rating = float(self.rating_var.get())
            model_type = self.model_var.get()

            self.status_label.configure(text="📊 Getting recommendations...")

            if model_type == "Collaborative":
                if not self.cf_model.trained_models:
                    messagebox.showwarning("Error", "Please train models first!")
                    return
                recs = self.cf_model.get_user_recommendations(
                    1, model_name='svd', n=n,
                    genre=genre, year=year, min_rating=min_rating
                )
            elif model_type == "Content-Based":
                if self.cb_model.similarity_matrix is None:
                    messagebox.showwarning("Error", "Please train models first!")
                    return
                recs = self.cb_model.get_user_recommendations(
                    1, n=n,
                    genre=genre, year=year, min_rating=min_rating
                )
            else:
                if not self.cf_model.trained_models or self.cb_model.similarity_matrix is None:
                    messagebox.showwarning("Error", "Please train models first!")
                    return
                recs = self.hybrid_model.get_hybrid_recommendations(
                    1, n=n, alpha=0.6,
                    genre=genre, year=year, min_rating=min_rating
                )

            self.movie_listbox.delete(0, tk.END)
            self.movie_ids = {}

            if not recs:
                self.movie_listbox.insert(tk.END, "No movies found with these filters!")
                self.status_label.configure(text="❌ No movies found!")
                return

            for idx, movie in enumerate(recs):
                title = movie.get('title', 'Unknown')
                rating = movie.get('avg_rating', 0)
                display_text = f"⭐ {title[:50]} | {rating:.1f} ★"
                self.movie_listbox.insert(tk.END, display_text)
                self.movie_ids[idx] = movie['movie_id']

            self.status_label.configure(text=f"✅ {len(recs)} movies shown!")

        except Exception as e:
            self.status_label.configure(text=f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Error getting recommendations:\n{str(e)}")

    def on_movie_select(self, event):
        try:
            selection = self.movie_listbox.curselection()
            if not selection:
                return

            index = selection[0]
            movie_text = self.movie_listbox.get(index)

            if "No movies" in movie_text:
                return

            movie_id = self.movie_ids.get(index)

            if movie_id:
                info = self.data_loader.get_movie_info(movie_id)
                if info:
                    self.show_movie_details(info)
        except Exception as e:
            print(f"Error selecting movie: {e}")

    def show_movie_details(self, info):
        self.movie_info_text.delete("1.0", "end")

        details = f"🎬 {info['title']}\n"
        details += "=" * 40 + "\n"
        details += f"📅 Year: {info['year'] if info['year'] else 'N/A'}\n"
        details += f"🎭 Genres: {', '.join(info['genres'])}\n"
        details += f"⭐ Average Rating: {info['avg_rating']:.2f}/5\n"

        ratings = self.data_loader.get_movie_ratings(info['movie_id'])
        details += f"📊 Total Ratings: {len(ratings)}\n"

        self.movie_info_text.insert("end", details)

    def train_models_thread(self):
        if not self.is_loaded:
            messagebox.showwarning("Error", "Dataset not loaded!")
            return

        self.status_label.configure(text="🤖 Training models...")
        self.progress_bar.set(0.1)

        def train():
            try:
                self.add_chat_message("system", "🤖 Starting model training...")

                self.status_label.configure(text="🎯 Training Collaborative...")
                self.cf_model.train_svd()
                self.progress_bar.set(0.3)
                self.cf_model.train_knn()
                self.progress_bar.set(0.5)
                self.cf_model.train_nmf()
                self.progress_bar.set(0.6)

                self.status_label.configure(text="🎨 Training Content-Based...")
                self.cb_model.prepare_content_features()
                self.progress_bar.set(0.8)

                self.hybrid_model.set_models(self.cf_model, self.cb_model)
                self.progress_bar.set(1.0)

                best_model, best_rmse = self.cf_model.get_best_model()

                self.status_label.configure(text="✅ All models trained!")
                self.add_chat_message(
                    "system",
                    f"✅ Training complete! Best model: {best_model} (RMSE: {best_rmse:.4f})"
                )

                messagebox.showinfo("Success", "✅ All models trained successfully!")

            except Exception as e:
                self.status_label.configure(text=f"❌ Error: {str(e)}")
                self.add_chat_message("system", f"❌ Error: {str(e)}")
                messagebox.showerror("Error", f"Error training models:\n{str(e)}")

        thread = threading.Thread(target=train)
        thread.daemon = True
        thread.start()

    def send_chat_message(self):
        user_input = self.chat_input.get().strip()

        if not user_input:
            return

        self.add_chat_message("user", user_input)
        self.chat_input.delete(0, tk.END)

        threading.Thread(target=self.process_chat_query, args=(user_input,), daemon=True).start()

    def process_chat_query(self, query):
        # Use the chatbot to process
        response = self.chatbot.process_query(query)
        self.add_chat_message("bot", response)

        # Also update recommendations if movie-related
        if self.data_loader and any(k in query.lower() for k in ['recommend', 'show', 'find', 'search']):
            try:
                genre = self.chatbot.extract_genre(query)
                year = self.chatbot.extract_year(query)
                rating = self.chatbot.extract_rating(query)
                count = self.chatbot.extract_count(query)

                recs = self.data_loader.get_popular_movies(
                    n=count,
                    genre=genre,
                    year=year,
                    min_rating=rating if rating else 0
                )

                if recs:
                    self.window.after(0, lambda: self.update_listbox_from_recs(recs))
            except:
                pass

    def update_listbox_from_recs(self, recs):
        self.movie_listbox.delete(0, tk.END)
        self.movie_ids = {}

        for idx, movie in enumerate(recs[:30]):
            title = movie.get('title', 'Unknown')
            rating = movie.get('avg_rating', 0)
            display_text = f"⭐ {title[:50]} | {rating:.1f} ★"
            self.movie_listbox.insert(tk.END, display_text)
            self.movie_ids[idx] = movie['movie_id']

    def add_chat_message(self, sender, message):
        self.chat_display.configure(state="normal")

        if sender == "user":
            self.chat_display.insert("end", f"🧑 You: {message}\n\n")
        elif sender == "bot":
            self.chat_display.insert("end", f"🤖 Assistant:\n{message}\n\n")
        else:
            self.chat_display.insert("end", f"💬 {message}\n\n")

        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = MovieChatbotApp()
    app.run()