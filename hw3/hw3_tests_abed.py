import os

from hw3 import LoginManager, DBManager


def main():
    login_manager = LoginManager()
    db_manager = DBManager()

    while True:
        print("\nMenu:")
        print("1. Register User")
        print("2. Login User")
        print("3. Load Games from CSV")
        print("4. Rent a Game")
        print("5. Return a Game")
        print("6. Recommend Games by Genre")
        print("7. Recommend Games by Name")
        print("8. Find Top Rated Games")
        print("9. Decrement Scores for Platform")
        print("10. Get Average Score per Platform")
        print("11. Get Genres Distribution")
        print("12. Exit")

        choice = input("Enter your choice: ")

        try:
            if choice == "1":
                username = input("Enter username: ")
                password = input("Enter password: ")
                login_manager.register_user(username, password)
                print(f"User '{username}' registered successfully.")

            elif choice == "2":
                username = input("Enter username: ")
                password = input("Enter password: ")
                user = login_manager.login_user(username, password)
                print(f"Logged in as: {user['username']}")

            elif choice == "3":


                    db_manager.load_csv()
                    print("Games loaded successfully from CSV.")


            elif choice == "4":
                username = input("Enter username: ")
                password = input("Enter password: ")
                user = login_manager.login_user(username, password)
                game_title = input("Enter the game title to rent: ")
                result = db_manager.rent_game(user, game_title)
                print(result)

            elif choice == "5":
                username = input("Enter username: ")
                password = input("Enter password: ")
                user = login_manager.login_user(username, password)
                game_title = input("Enter the game title to return: ")
                result = db_manager.return_game(user, game_title)
                print(result)

            elif choice == "6":
                username = input("Enter username: ")
                password = input("Enter password: ")
                user = login_manager.login_user(username, password)
                recommendations = db_manager.recommend_games_by_genre(user)
                print("Recommended Games by Genre:", recommendations)

            elif choice == "7":
                username = input("Enter username: ")
                password = input("Enter password: ")
                user = login_manager.login_user(username, password)
                recommendations = db_manager.recommend_games_by_name(user)
                print("Recommended Games by Name:", recommendations)

            elif choice == "8":
                min_score = float(input("Enter the minimum user score: "))
                top_games = db_manager.find_top_rated_games(min_score)
                print("Top Rated Games:")
                count = 1

                for game in top_games:
                    print(count, game)
                    count+=1

            elif choice == "9":
                platform_name = input("Enter the platform name: ")
                db_manager.decrement_scores(platform_name)
                print(f"Scores decremented for platform '{platform_name}'.")

            elif choice == "10":
                averages = db_manager.get_average_score_per_platform()
                print("Average Score per Platform:")
                for platform, avg_score in averages.items():
                    print(f"{platform}: {avg_score:.3f}")

            elif choice == "11":
                distribution = db_manager.get_genres_distribution()
                print("Genres Distribution:")
                for genre, count in distribution.items():
                    print(f"{genre}: {count}")

            elif choice == "12":
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please try again.")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()