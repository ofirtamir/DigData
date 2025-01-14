import pymongo
import bcrypt
import ast
import pandas as pd
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class LoginManager:

    def __init__(self) -> None:
        # MongoDB connection
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["hw3"]
        self.collection = self.db["users"]
        self.salt = b"$2b$12$ezgTynDsK3pzF8SStLuAPO"  # TODO: if not working, generate a new salt

    def register_user(self, username: str, password: str) -> None:
        # Validate username and password are not empty
        if not username or not password:
            raise ValueError("Username and password are required.")

        # Validate username and password are at least 3 characters long
        if len(username) < 3 or len(password) < 3:
            raise ValueError("Username and password must be at least 3 characters.")

        # Check if the username already exists in the database
        if self.collection.find_one({"username": username}):
            raise ValueError(f"User already exists: {username}.")

        # Hash the password with bcrypt
        hashed_password = bcrypt.hashpw(password.encode(), self.salt)

        # Insert the new user into the collection
        self.collection.insert_one({
            "username": username,
            "password": hashed_password.decode(),  # Decode to save as a string
            "rented_games_ids": []  # Initialize rented games as an empty list
        })
        

    def login_user(self, username: str, password: str) -> object:
        # Validate username and password are not empty
        if not username or not password:
            raise ValueError("Username and password are required.")

        # Hash the provided password using the same salt
        hashed_password = bcrypt.hashpw(password.encode(), self.salt).decode()

        # Query the database for a user with the provided username and hashed password
        user = self.collection.find_one({"username": username, "password": hashed_password})

        if user:
            print(f"Logged in successfully as: {username}")
            return user
        else:
            raise ValueError("Invalid username or password")



class DBManager:

    def __init__(self) -> None:
        # MongoDB connection
        self.client =  pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["hw3"]
        self.user_collection = self.db["users"]
        self.game_collection = self.db["games"]

    def load_csv(self) -> None:
        # Open the CSV file
        with open("NintendoGames.csv", "r", encoding="utf-8") as csv_file:
            data = pd.read_csv("NintendoGames.csv")

            data["genres"] = data["genres"].apply(ast.literal_eval)
            data["is_rented"] = False
            
            records = data.to_dict(orient="records")
            
            # Insert records into games collection without duplicates
            for record in records:
                if not self.game_collection.find_one({"title": record["title"]}):
                    self.game_collection.insert_one(record)

    def rent_game(self, user: dict, game_title: str) -> str:
        # Find the game by title
        game = self.game_collection.find_one({"title": game_title})
        
        if not game:
            return f"{game_title} not found"
        
        if game.get("is_rented", False):
            return f"{game_title} is already rented"
        
        # Update the game to mark it as rented
        self.game_collection.update_one(
            {"_id": game["_id"]}, {"$set": {"is_rented": True}}
        )
        
        # Update the user's rented games list
        self.user_collection.update_one(
            {"_id": user["_id"]},
            {"$push": {"rented_games_ids": game["_id"]}}
        )
        user["rented_games_ids"].append(game["_id"])
        
        return f"{game_title} rented successfully"


    def return_game(self, user: dict, game_title: str) -> str:
        # Find the game by title
        #TODO:1. Get the list of games ids rented by the user from the user object.
        game = self.game_collection.find_one({"title": game_title})
        
        if not game:
            return f"{game_title} was not rented by you"
            
        if game["_id"] not in user.get("rented_games_ids", []):
            return f"{game_title} was not rented by you"
        
        # Update the game to mark it as not rented
        self.game_collection.update_one(
            {"_id": game["_id"]}, {"$set": {"is_rented": False}}
        )
        
        # Update the user's rented games list
        self.user_collection.update_one(
            {"_id": user["_id"]},
            {"$pull": {"rented_games_ids": game["_id"]}}
        )
        user["rented_games_ids"].remove(game["_id"])
        return f"{game_title} returned successfully"


    def recommend_games_by_genre(self, user: dict) -> list:
        # Retrieve rented games by the user
        rented_games_ids = user.get("rented_games_ids", [])
        if not rented_games_ids:
            return ["No games rented"]

        rented_games = list(self.game_collection.find({"_id": {"$in": rented_games_ids}}))
        
        # Count the genres frequency
        genre_count = {}
        for game in rented_games:
            for genre in game.get("genres", []):
                genre_count[genre] = genre_count.get(genre, 0) + 1
        
        if not genre_count:
            return []

        # Select a genre randomly based on frequency
        genres, weights = zip(*genre_count.items())
        chosen_genre = random.choices(genres, weights=weights, k=1)[0]

        # print(f"Chosen genre: {chosen_genre}")  # Debugging
        # print(f"Available games: {list(self.game_collection.find({'genres': chosen_genre, 'is_rented': False}))}")  # Debugging

        # Find games with the chosen genre that are not rented or owned
        recommendations = list(self.game_collection.find({
            "genres": chosen_genre,
            "is_rented": False,
            "_id": {"$nin": rented_games_ids}
        }).limit(5))

        return [game["title"] for game in recommendations]


    def recommend_games_by_name(self, user: dict) -> list:
        # Retrieve rented games by the user
        rented_games_ids = user.get("rented_games_ids", [])
        if not rented_games_ids:
            return ["No games rented"]

        rented_games = list(self.game_collection.find({"_id": {"$in": rented_games_ids}}))
        
        # Choose a random rented game
        chosen_game = random.choice(rented_games)
        chosen_title = chosen_game["title"]

        # Retrieve all game titles
        all_games = list(self.game_collection.find({"_id": {"$nin": rented_games_ids}, "is_rented": False}))
        all_titles = [game["title"] for game in all_games]

        if not all_titles:
            return []

        # Add the chosen game title to the list of titles for similarity computation
        all_titles.append(chosen_title)

        # Compute TF-IDF vectors for all titles
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(all_titles)

        # Compute cosine similarity
        cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

        # Find the top 5 most similar titles
        similar_indices = cosine_sim.argsort()[-5:][::-1]
        recommendations = [all_games[i]["title"] for i in similar_indices]

        return recommendations


    def find_top_rated_games(self, min_score) -> list:
        #min_score is a double
        # Query to find games with user_score as string and compare as numbers
        top_games = list(self.game_collection.find(
            {
                "$expr": {
                    "$gte": [
                        {"$toDouble": "$user_score"},  # Convert user_score to double
                        min_score
                    ]
                }
            },
            {"title": 1, "user_score": 1, "_id": 0}
        ))

        return top_games


    def decrement_scores(self, platform_name) -> None:
        # Update user scores for the specified platform
        self.game_collection.update_many(
            {"platform": platform_name, "user_score": {"$gt": 0}},
            {"$inc": {"user_score": -1}}
        )

        # Ensure no scores are below 0
        self.game_collection.update_many(
            {"platform": platform_name, "user_score": {"$lt": 0}},
            {"$set": {"user_score": 0}}
        )


    def get_average_score_per_platform(self) -> dict:
        # Use aggregation to calculate the average user_score for each platform
        pipeline = [
            {"$group": {
                "_id": "$platform",
                "average_score": {"$avg": "$user_score"}
            }}
        ]
        results = list(self.game_collection.aggregate(pipeline))
        
        # Convert the results to a dictionary
        averages = {result["_id"]: round(result["average_score"], 3) for result in results}
        return averages


    def get_genres_distribution(self) -> dict:
        # Use aggregation to calculate the distribution of genres
        pipeline = [
            {"$unwind": "$genres"},  # Unwind the genres array
            {"$group": {
                "_id": "$genres",
                "count": {"$sum": 1}
            }}
        ]
        results = list(self.game_collection.aggregate(pipeline))
        
        # Convert the results to a dictionary
        distribution = {result["_id"]: result["count"] for result in results}
        return distribution


