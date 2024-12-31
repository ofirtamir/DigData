import unittest
from hw3 import LoginManager, DBManager
import pymongo
import ast
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TestLoginManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up MongoDB connection
        cls.client = pymongo.MongoClient("mongodb://localhost:27017/")
        cls.db = cls.client["hw3"]
        cls.users_collection = cls.db["users"]
        cls.games_collection = cls.db["games"]
        cls.login_manager = LoginManager()
        cls.login_manager.client = cls.client  # Share the MongoDB client instance
        cls.login_manager.collection = cls.users_collection  # Share the users collection

    def setUp(self):
        # Clean up the users collection before each test
        self.users_collection.delete_many({})
        self.games_collection.delete_many({})


    def test_register_user_success(self):
        self.login_manager.register_user("testuser", "password123")
        user = self.users_collection.find_one({"username": "testuser"})
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "testuser")

    def test_register_user_duplicate(self):
        self.login_manager.register_user("duplicateuser", "password123")
        with self.assertRaises(ValueError) as context:
            self.login_manager.register_user("duplicateuser", "password456")
        self.assertEqual(str(context.exception), "User already exists: duplicateuser.")

    def test_register_user_invalid_input(self):
        with self.assertRaises(ValueError) as context:
            self.login_manager.register_user("", "")
        self.assertEqual(str(context.exception), "Username and password are required.")

    def test_register_user_short_input(self):
        with self.assertRaises(ValueError) as context:
            self.login_manager.register_user("ab", "12")
        self.assertEqual(str(context.exception), "Username and password must be at least 3 characters.")

    def test_login_user_success(self):
        # Register a test user
        self.login_manager.register_user("testuser", "password123")

        # Attempt to login with correct credentials
        user = self.login_manager.login_user("testuser", "password123")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "testuser")

    def test_login_user_invalid_username(self):
        with self.assertRaises(ValueError) as context:
            self.login_manager.login_user("nonexistentuser", "password123")
        self.assertEqual(str(context.exception), "Invalid username or password")

    def test_login_user_invalid_password(self):
        # Register a test user
        self.login_manager.register_user("testuser2", "correctpassword")

        # Attempt to login with incorrect password
        with self.assertRaises(ValueError) as context:
            self.login_manager.login_user("testuser2", "wrongpassword")
        self.assertEqual(str(context.exception), "Invalid username or password")

    def test_login_user_empty_input(self):
        with self.assertRaises(ValueError) as context:
            self.login_manager.login_user("", "")
        self.assertEqual(str(context.exception), "Username and password are required.")

    def test_load_csv(self):
        # Ensure the game collection is empty before loading
        self.games_collection.delete_many({})

        # Run the function
        db_manager = DBManager(client=self.client)  # Pass shared client
        db_manager.load_csv()

        # Check if data was loaded
        games = list(self.games_collection.find())
        self.assertGreater(len(games), 0)  # Ensure games were added

        # Check specific fields in the data
        for game in games:
            # Ensure "title" exists
            self.assertIn("title", game)
            # Ensure "genres" is a list
            self.assertIsInstance(game["genres"], list)
            # Ensure "is_rented" is False
            self.assertIn("is_rented", game)
            self.assertFalse(game["is_rented"])

    def test_load_csv_no_duplicates(self):
        db_manager = DBManager(client=self.client)  # Pass shared client
        db_manager.load_csv()
        initial_count = self.games_collection.count_documents({})

        # Run load_csv again
        db_manager.load_csv()
        new_count = self.games_collection.count_documents({})

        # Ensure no duplicates
        self.assertEqual(initial_count, new_count)

    def test_rent_game_success(self):
        # Add a user and a game
        user = {"username": "testuser", "rented_games": []}
        self.users_collection.insert_one(user)
        game = {"title": "Pikmin 4", "is_rented": False, "genres": ["Strategy"]}
        self.games_collection.insert_one(game)

        # Rent the game
        user_from_db = self.users_collection.find_one({"username": "testuser"})
        game_title = "Pikmin 4"
        db_manager = DBManager(client=self.client)
        result = db_manager.rent_game(user_from_db, game_title)

        self.assertEqual(result, "Pikmin 4 rented successfully")
        updated_game = self.games_collection.find_one({"title": "Pikmin 4"})
        self.assertTrue(updated_game["is_rented"])
        updated_user = self.users_collection.find_one({"username": "testuser"})
        self.assertIn(updated_game["_id"], updated_user["rented_games"])

    def test_rent_game_already_rented(self):
        # Add a user and a rented game
        user = {"username": "testuser", "rented_games": []}
        self.users_collection.insert_one(user)
        game = {"title": "Pikmin 4", "is_rented": True, "genres": ["Strategy"]}
        self.games_collection.insert_one(game)

        # Try to rent the already rented game
        user_from_db = self.users_collection.find_one({"username": "testuser"})
        game_title = "Pikmin 4"
        db_manager = DBManager(client=self.client)
        result = db_manager.rent_game(user_from_db, game_title)

        self.assertEqual(result, "Pikmin 4 is already rented")

    def test_rent_game_not_found(self):
        # Add a user
        user = {"username": "testuser", "rented_games": []}
        self.users_collection.insert_one(user)

        # Try to rent a non-existing game
        user_from_db = self.users_collection.find_one({"username": "testuser"})
        game_title = "Nonexistent Game"
        db_manager = DBManager(client=self.client)
        result = db_manager.rent_game(user_from_db, game_title)

        self.assertEqual(result, "Nonexistent Game not found")

    def test_return_game_success(self):
        # Add a user and a rented game
        user = {"username": "testuser", "rented_games": []}
        self.users_collection.insert_one(user)
        game = {"title": "Pikmin 4", "is_rented": True, "genres": ["Strategy"]}
        self.games_collection.insert_one(game)

        # Associate the game with the user
        self.users_collection.update_one(
            {"username": "testuser"},
            {"$push": {"rented_games": game["_id"]}}
        )

        # Return the game
        user_from_db = self.users_collection.find_one({"username": "testuser"})
        game_title = "Pikmin 4"
        db_manager = DBManager(client=self.client)
        result = db_manager.return_game(user_from_db, game_title)

        self.assertEqual(result, "Pikmin 4 returned successfully")
        updated_game = self.games_collection.find_one({"title": "Pikmin 4"})
        self.assertFalse(updated_game["is_rented"])
        updated_user = self.users_collection.find_one({"username": "testuser"})
        self.assertNotIn(updated_game["_id"], updated_user["rented_games"])

    def test_return_game_not_rented(self):
        # Add a user and a game
        user = {"username": "testuser", "rented_games": []}
        self.users_collection.insert_one(user)
        game = {"title": "Pikmin 4", "is_rented": False, "genres": ["Strategy"]}
        self.games_collection.insert_one(game)

        # Try to return the game
        user_from_db = self.users_collection.find_one({"username": "testuser"})
        game_title = "Pikmin 4"
        db_manager = DBManager(client=self.client)
        result = db_manager.return_game(user_from_db, game_title)

        self.assertEqual(result, "Pikmin 4 was not rented by you")

    def test_recommend_games_by_genre_success(self):
        # Add a user and rented games
        user = {"username": "testuser", "rented_games": []}
        self.users_collection.insert_one(user)
        rented_game = {
            "title": "Pikmin 4",
            "is_rented": True,
            "genres": ["Strategy", "Adventure"]
        }
        self.games_collection.insert_one(rented_game)
        self.users_collection.update_one(
            {"username": "testuser"},
            {"$push": {"rented_games": rented_game["_id"]}}
        )

        # Add additional games in the same genre
        for i in range(15):  # Ensure there are enough games to recommend
            self.games_collection.insert_one({
                "title": f"Game {i}",
                "is_rented": False,
                "genres": ["Strategy"]
            })

        # Recommend games
        user_from_db = self.users_collection.find_one({"username": "testuser"})
        db_manager = DBManager(client=self.client)
        recommendations = db_manager.recommend_games_by_genre(user_from_db)

        # print(f"Recommendations: {recommendations}")  # Debugging
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(all(isinstance(game, str) for game in recommendations))

    def test_recommend_games_by_genre_no_rented(self):
        # Add a user without rented games
        user = {"username": "testuser", "rented_games": []}
        self.users_collection.insert_one(user)

        user_from_db = self.users_collection.find_one({"username": "testuser"})
        db_manager = DBManager(client=self.client)
        recommendations = db_manager.recommend_games_by_genre(user_from_db)

        self.assertEqual(recommendations, "No games rented")

    def test_recommend_games_by_name_success(self):
        # Add a user and rented games
        user = {"username": "testuser", "rented_games": []}
        self.users_collection.insert_one(user)
        rented_game = {
            "title": "Pikmin 4",
            "is_rented": True,
            "genres": ["Strategy"]
        }
        self.games_collection.insert_one(rented_game)
        self.users_collection.update_one(
            {"username": "testuser"},
            {"$push": {"rented_games": rented_game["_id"]}}
        )

        # Add additional games
        for i in range(10):
            self.games_collection.insert_one({
                "title": f"Game {i}",
                "is_rented": False,
                "genres": ["Adventure"]
            })

        # Recommend games
        user_from_db = self.users_collection.find_one({"username": "testuser"})
        db_manager = DBManager(client=self.client)
        recommendations = db_manager.recommend_games_by_name(user_from_db)

        self.assertGreater(len(recommendations), 0)
        self.assertTrue(all(isinstance(game, str) for game in recommendations))

    def test_recommend_games_by_name_no_rented(self):
        # Add a user without rented games
        user = {"username": "testuser", "rented_games": []}
        self.users_collection.insert_one(user)

        user_from_db = self.users_collection.find_one({"username": "testuser"})
        db_manager = DBManager(client=self.client)
        recommendations = db_manager.recommend_games_by_name(user_from_db)

        self.assertEqual(recommendations, "No games rented")

    def test_find_top_rated_games_success(self):
        # Add sample games
        games = [
            {"title": "Game A", "user_score": 9.5, "is_rented": False},
            {"title": "Game B", "user_score": 8.0, "is_rented": False},
            {"title": "Game C", "user_score": 7.5, "is_rented": False},
            {"title": "Game D", "user_score": 6.0, "is_rented": False}
        ]
        self.games_collection.insert_many(games)

        # Find games with user_score >= 8.0
        db_manager = DBManager(client=self.client)
        top_games = db_manager.find_top_rated_games(8.0)

        self.assertEqual(len(top_games), 2)
        self.assertIn({"title": "Game A", "user_score": 9.5}, top_games)
        self.assertIn({"title": "Game B", "user_score": 8.0}, top_games)

    def test_find_top_rated_games_no_results(self):
        # Add sample games with low scores
        games = [
            {"title": "Game E", "user_score": 4.5, "is_rented": False},
            {"title": "Game F", "user_score": 5.0, "is_rented": False}
        ]
        self.games_collection.insert_many(games)

        # Find games with user_score >= 8.0
        db_manager = DBManager(client=self.client)
        top_games = db_manager.find_top_rated_games(8.0)

        self.assertEqual(len(top_games), 0)
    def test_decrement_scores(self):
        # Add sample games for a platform
        games = [
            {"title": "Game A", "platform": "Nintendo Switch", "user_score": 10},
            {"title": "Game B", "platform": "Nintendo Switch", "user_score": 5},
            {"title": "Game C", "platform": "Nintendo Switch", "user_score": 0},
            {"title": "Game D", "platform": "PlayStation", "user_score": 8}
        ]
        self.games_collection.insert_many(games)

        # Decrement scores for "Nintendo Switch"
        db_manager = DBManager(client=self.client)
        db_manager.decrement_scores("Nintendo Switch")

        # Verify scores were decremented
        updated_games = list(self.games_collection.find({"platform": "Nintendo Switch"}))
        self.assertEqual(updated_games[0]["user_score"], 9)  # Game A
        self.assertEqual(updated_games[1]["user_score"], 4)  # Game B
        self.assertEqual(updated_games[2]["user_score"], 0)  # Game C (remains 0)

        # Verify scores for other platforms are unchanged
        other_game = self.games_collection.find_one({"platform": "PlayStation"})
        self.assertEqual(other_game["user_score"], 8)
    
    def test_get_average_score_per_platform(self):
        # Add sample games
        games = [
            {"title": "Game A", "platform": "Nintendo Switch", "user_score": 8.5},
            {"title": "Game B", "platform": "Nintendo Switch", "user_score": 7.0},
            {"title": "Game C", "platform": "PlayStation", "user_score": 9.0},
            {"title": "Game D", "platform": "PlayStation", "user_score": 8.0},
        ]
        self.games_collection.insert_many(games)

        # Calculate average scores
        db_manager = DBManager(client=self.client)
        averages = db_manager.get_average_score_per_platform()

        # Validate results
        self.assertAlmostEqual(averages["Nintendo Switch"], 7.75, places=2)
        self.assertAlmostEqual(averages["PlayStation"], 8.5, places=2)
    
    def test_get_genres_distribution(self):
        # Add sample games with multiple genres
        games = [
            {"title": "Game A", "genres": ["Action", "Adventure"]},
            {"title": "Game B", "genres": ["Action", "Strategy"]},
            {"title": "Game C", "genres": ["Adventure", "Puzzle"]},
            {"title": "Game D", "genres": ["Puzzle"]}
        ]
        self.games_collection.insert_many(games)

        # Calculate genres distribution
        db_manager = DBManager(client=self.client)
        distribution = db_manager.get_genres_distribution()

        # Validate the distribution
        self.assertEqual(distribution["Action"], 2)
        self.assertEqual(distribution["Adventure"], 2)
        self.assertEqual(distribution["Strategy"], 1)
        self.assertEqual(distribution["Puzzle"], 2)

    @classmethod
    def tearDownClass(cls):
        # Clean up MongoDB after all tests
        cls.users_collection.delete_many({})
        cls.games_collection.delete_many({})
        cls.client.close()

if __name__ == "__main__":
    unittest.main()
