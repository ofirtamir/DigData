import pymongo
from hw3 import LoginManager, DBManager  # Assuming the classes are saved in login_db_manager.py

if __name__ == "__main__":
    # Initialize the login manager and DB manager
    login_manager = LoginManager()
    db_manager = DBManager()

    # Test register_user
    try:
        login_manager.register_user("test_user2", "password1234")
        print("User registered successfully.")
    except ValueError as e:
        print(f"Register test failed: {e}")

    # Test duplicate registration
    try:
        login_manager.register_user("test_user2", "password1234")
        print("Duplicate registration allowed (Error).")
    except ValueError as e:
        print(f"Duplicate registration test passed: {e}")

    # Test login_user
    try:
        user = login_manager.login_user("test_user2", "password1234")
        print(f"Login successful for user: {user['username']}")
    except ValueError as e:
        print(f"Login test failed: {e}")

    # Load the CSV file
    try:
        db_manager.load_csv()
        print("CSV data loaded successfully.")
    except Exception as e:
        print(f"Failed to load CSV: {e}")

    # Create a test user
    test_user = db_manager.user_collection.find_one({"username": "test_user2"})
    if not test_user:
        print("Test user not found. Ensure the user exists before proceeding.")
    else:
        # Test renting a game
        game_title = "Part Time UFO"
        rent_result = db_manager.rent_game(test_user, game_title)
        print(rent_result)

        # Test renting the same game again
        rent_result = db_manager.rent_game(test_user, game_title)
        print(rent_result)

        # Test renting a non-existing game
        rent_result = db_manager.rent_game(test_user, "Non-existent Game")
        print(rent_result)

        # Test returning the game
        return_result = db_manager.return_game(test_user, game_title)
        print(return_result)

        # Test returning a game not rented by the user
        return_result = db_manager.return_game(test_user, "Non-existent Game")
        print(return_result)

        # Test renting the same game again after returning it
        rent_result = db_manager.rent_game(test_user, game_title)
        print(rent_result)

        # Test recommendations by genre
        genre_recommendations = db_manager.recommend_games_by_genre(test_user)
        print("Genre recommendations:", genre_recommendations)

        # Test recommendations by name
        name_recommendations = db_manager.recommend_games_by_name(test_user)
        print("Name recommendations:", name_recommendations)

        # Test finding top-rated games
        top_rated = db_manager.find_top_rated_games(5)
        print("Top-rated games:", top_rated)

        # Test decrementing scores for a specific platform
        platform = "Switch"  # Replace with a valid platform from your CSV
        db_manager.decrement_scores(platform)
        print(f"Scores decremented for platform: {platform}")

        # Test calculating average scores per platform
        average_scores = db_manager.get_average_score_per_platform()
        print("Average scores per platform:", average_scores)

        # Test genre distribution
        genre_distribution = db_manager.get_genres_distribution()
        print("Genres distribution:", genre_distribution)
