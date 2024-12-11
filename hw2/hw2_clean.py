from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from sqlalchemy import func
import bcrypt

Base = declarative_base()


class User(Base):
    __tablename__ = "Users"
    # TODO

    def __init__(
        self,
        username,
        password,
        first_name,
        last_name,
        date_of_birth,
        registration_date,
    ):
        # TODO
        pass

    def add_history(self, media_item_id):
        # TODO
        pass

    def sum_title_length (self):
        # TODO
        pass


class MediaItem(Base):
    __tablename__ = "MediaItems"
    # TODO

    def __init__(self, title, prod_year, title_length):
        # TODO
        pass


class History(Base):
    __tablename__ = "History"
    # TODO

    def __init__(self, user_id, media_item_id, viewtime):
        # TODO
        pass


class Repository:
    def __init__(self, model_class):
        self.model_class=model_class

    def get_by_id(self, session, entity_id):
        return session.query(self.model_class).filter(self.model_class.id == entity_id).first()
    
    def get_all(self,session):
        return session.query(self.model_class).all()
    
    def delete(self,session, entity):
        session.delete(entity)

    def add(self, session, entity):
        session.add(entity)

class UserRepository(Repository):
    def __init__(self):
        super().__init__(User)
   
    def validateUser(self,session, username: str, password: str) -> bool:
        # TODO
        pass
    
    def getNumberOfRegistredUsers(self,session, n: int) -> int:
        # TODO
        pass
    
class ItemRepository(Repository):
    def __init__(self):
        super().__init__(MediaItem)

    def getTopNItems(self, session, top_n: int) -> list:
        # TODO
        pass
    

    
class UserService:
    def __init__(self, session, user_repo: UserRepository):
        self.user_repo = user_repo
        self.session = session

    def create_user(self, username, password, first_name, last_name, date_of_birth):
        # TODO
        pass

    def add_history_to_user(self, username, media_item_id):
        # TODO
        pass
    
    def validateUser(self, username: str, password: str) -> bool:
        # TODO
        pass

    def getNumberOfRegistredUsers(self, n: int) -> int:
        # TODO
        pass
    
    def sum_title_length_to_user(self, username):
        # TODO
        pass

    def get_all_users(self):
        # TODO
        pass
    

class ItemService:
    def __init__(self, session, item_repo:ItemRepository):
        self.item_repo=item_repo
        self.session = session

    def create_item(self, title, prod_year):
        # TODO
        pass

# username=''
# password=''
# connection_string = f"mssql+pyodbc://{username}:{password}@132.72.64.124/{username}?driver=ODBC+Driver+17+for+SQL+Server"
# engine = create_engine(connection_string)
# Base.metadata.create_all(engine)
# session = sessionmaker(bind=engine)()