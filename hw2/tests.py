import unittest
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from hw2 import Base, User, MediaItem, History, UserRepository, ItemRepository, UserService
from datetime import datetime, timedelta
import warnings



class TestHW2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
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
        self.session.execute(delete(User))
        self.session.execute(delete(MediaItem))
        self.session.execute(delete(History))
        self.session.commit()
        # Rollback any uncommitted changes after each test to ensure no data persists
        self.session.close()

    @classmethod
    def tearDownClass(cls):
        # Drop all tables after the tests to clean up the database schema
        Base.metadata.drop_all(cls.engine)

    # ------------ Tests for Repositories ------------
    # tests for User

    def test_create_user(self):
        User(username="test_user", password="password123", first_name="John", last_name="Doe", date_of_birth=datetime(1990, 1, 1))

    def test_user_add_history(self):
        # TODO
        pass

    def test_user_sum_title_length(self):
        # TODO
        pass

    # test for MediaItem

    def test_create_media_item(self):
        MediaItem(title="Test Movie", prod_year=2022)

    # test for History

    def test_create_history(self):
        History(user_id="test_user", media_item_id="Test Movie", viewtime=datetime.now())

    # ------------ Tests for Repositories ------------
    # tests for User Repository

    def test_user_repository_validate_user(self):
        #TODO
        pass

    def test_user_repository_get_number_of_registred_users(self):
        #TODO
        pass

    # tests for Item Repository

    def test_item_repository_get_top_n_items(self):
        #TODO
        pass
    
    # ------------ Tests for Services ------------
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

    def test_add_history_to_user(self):
        #TODO
        pass

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

    def test_get_number_of_registred_users_add_user(self):
        self.assertEqual(self.user_service.getNumberOfRegistredUsers(10), 0)
        self.user_service.create_user(
            username="test_user",
            password="password123",
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1990, 1, 1)
        )
        self.assertEqual(self.user_service.getNumberOfRegistredUsers(10), 1)

    def test_get_number_of_registred_users_cutoff_data(self):
        self.assertEqual(self.user_service.getNumberOfRegistredUsers(10), 0)
        self.user_service.create_user(
            username="test_user",
            password="password123",
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1990, 1, 1)
        )

        user = self.session.query(User).filter_by(id="test_user").first()
        if user is None:
            self.fail("User not found in the session")
        
        # Update the registration date to 2 weeks ago
        user.registration_date = datetime.utcnow() - timedelta(weeks=2)
        self.session.commit()
        self.assertEqual(self.user_service.getNumberOfRegistredUsers(10), 0)
    

    def test_sum_title_length_to_user(self):
        #TODO
        pass
    
    def test_get_all_users(self):
        self.assertEqual(len(self.user_service.get_all_users()), 0)
        self.user_service.create_user(
            username="test_user",
            password="password123",
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1990, 1, 1)
        )
        self.assertEqual(len(self.user_service.get_all_users()), 1)
        self.user_service.create_user(
            username="test_user2",
            password="password123",
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1990, 1, 1)
        )
        self.assertEqual(len(self.user_service.get_all_users()), 2)

    # tests for Item Service
    def test_create_item(self):
        #TODO
        pass


        

if __name__ == "__main__":
    unittest.main()
