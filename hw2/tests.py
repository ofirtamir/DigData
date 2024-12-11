import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from hw2 import Base, User, MediaItem, History, UserRepository, ItemRepository, UserService
from datetime import datetime, timedelta

class TestHW2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up the session class but do not create the in-memory database yet
        cls.engine = create_engine("sqlite:///:memory:")  # In-memory database for each test
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        # Create a fresh schema for each test to ensure no data from previous tests exists
        Base.metadata.create_all(self.engine)
        
        # Create a fresh session for each test to avoid data retention across tests
        self.session = self.Session()
        
        # Initialize repositories and services
        self.user_repo = UserRepository()
        self.item_repo = ItemRepository()
        self.user_service = UserService(self.session, self.user_repo)

    def tearDown(self):
        # Rollback any uncommitted changes after each test to ensure no data persists
        self.session.close()

    @classmethod
    def tearDownClass(cls):
        # Drop all tables after the tests to clean up the database schema
        Base.metadata.drop_all(cls.engine)


    def test_create_user(self):
        User(username="test_user", password="password123", first_name="John", last_name="Doe", date_of_birth=datetime(1990, 1, 1))

    def test_create_media_item(self):
        MediaItem(title="Test Movie", prod_year=2022)

    def test_create_history(self):
        History(user_id="test_user", media_item_id="Test Movie", viewtime=datetime.now())
    
    # tests for User Service

    def test_create_user_service_and_add_user(self):
        self.user_service.create_user(
            username="test_user1",
            password="password123",
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1990, 1, 1)
        )

        user = self.session.query(User).filter_by(id="test_user1").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, "John")

    def test_validate_user(self):
        self.user_service.create_user(
            username="test_user2",
            password="password123",
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1990, 1, 1)
        )

        self.assertTrue(self.user_service.validateUser("test_user2", "password123"))
        self.assertFalse(self.user_service.validateUser("test_user2", "wrong_password"))

    # def test_get_number_of_registred_users(self):
    #     self.user_service.create_user(
    #         username="test_user",
    #         password="password123",
    #         first_name="John",
    #         last_name="Doe",
    #         date_of_birth=datetime(1990, 1, 1)
    #     )
    #     self.assertEqual(self.user_service.getNumberOfRegistredUsers(1), 1)
    #     self.user_service.create_user(
    #         username="test_user2",
    #         password="password123",
    #         first_name="John",
    #         last_name="Doe",
    #         date_of_birth=datetime(1990, 1, 1)
    #     )
    #     self.assertEqual(self.user_service.getNumberOfRegistredUsers(2), 2)
    
    # def test_get_all_users():
    #     self.user_service.create_user(
    #         username="test_user",
    #         password="password123",
    #         first_name="John",
    #         last_name="Doe",
    #         date_of_birth=datetime(1990, 1, 1)
    #     )
    #     self.user_service.create_user(
    #         username="test_user2",
    #         password="password123",
    #         first_name="John",
    #         last_name="Doe",
    #         date_of_birth=datetime(1990, 1, 1)
    #     )
    #     self.assertEqual(self.user_service.getAllUsers(), 2)

        

if __name__ == "__main__":
    unittest.main()
