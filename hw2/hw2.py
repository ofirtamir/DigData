from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, LargeBinary
from sqlalchemy.orm import sessionmaker, relationship,declarative_base
from datetime import datetime, timedelta
from sqlalchemy import func
import bcrypt
from sqlalchemy.orm import Session

Base = declarative_base()


class User(Base):
    __tablename__ = "Users"
    id = Column(String(255), primary_key=True)  # username
    password = Column(LargeBinary, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    registration_date = Column( DateTime, default=datetime.utcnow, nullable=False)
    histories = relationship("History", back_populates="user", cascade="all, delete-orphan")


    def __init__(
        self,
        username,
        password,
        first_name,
        last_name,
        date_of_birth,
        registration_date,
    ):
        self.id = username
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.registration_date = registration_date

    def add_history(self, media_item_id):
        history = History(
            user_id=self.id, media_item_id=media_item_id, viewtime=datetime.now()
        )
        self.histories.append(history)

    def sum_title_length(self):
        total_length = 0
        for history in self.histories:
            if history.mediaitem.title_length:
                total_length += history.mediaitem.title_length
        return total_length



class MediaItem(Base):
    __tablename__ = "MediaItems"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    prod_year = Column(Integer, nullable=False)
    title_length = Column(Integer, nullable=False)

    histories = relationship("History", back_populates="mediaitem", cascade="all, delete-orphan")  # Fixed cascade behavior

    def __init__(self, title, prod_year):   
        self.title = title
        self.prod_year = prod_year
        self.title_length = len(title) 

class History(Base):
    __tablename__ = "History"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey("Users.id"), nullable=False)
    media_item_id = Column(Integer, ForeignKey("MediaItems.id"), nullable=False)
    viewtime = Column( DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="histories")
    mediaitem = relationship("MediaItem", back_populates="histories")

    def __init__(self, user_id, media_item_id, viewtime):   
        self.user_id = user_id
        self.media_item_id = media_item_id
        self.viewtime = viewtime
        self.mediaitem = None
        self.user = None

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
   
    def validateUser(self, session, username: str, password: str) -> bool:
        # Query the user from the database by username
        user = session.query(self.model_class).filter_by(id=username).first()
        if not user:
            return False

        # Compare the hashed password in the database with the provided password
        return bcrypt.checkpw(password.encode('utf-8'), user.password)

    def getNumberOfRegistredUsers(self, session, n: int) -> int:
        # Calculate the cutoff date
        cutoff_date = datetime.now() - timedelta(days=n)

        # Count the number of users registered in the past n days
        count = session.query(func.count(self.model_class.id)).filter(self.model_class.registration_date >= cutoff_date).scalar()
        return count
    
class ItemRepository(Repository):
    def __init__(self):
        super().__init__(MediaItem)

    def getTopNItems(self, session, top_n: int) -> list:
        # Retrieve the first top_n items in ascending order of id
        items = session.query(self.model_class).order_by(self.model_class.id.asc()).limit(top_n).all()
        return items
    
class UserService:
    def __init__(self, session, user_repo: UserRepository):
        self.user_repo = user_repo
        self.session = session

    def create_user(self, username, password, first_name, last_name, date_of_birth):
        user = User(username,password,first_name,last_name,date_of_birth,datetime.now())
        self.user_repo.add(self.session, user)
        self.session.commit()

    def add_history_to_user(self, username, media_item_id):
        user = self.user_repo.get_by_id(self.session, username)
        if user:
            user.add_history(media_item_id)
            self.session.commit()
        else:
            raise ValueError("User not found")

    def validateUser(self, username: str, password: str) -> bool:
        return self.user_repo.validateUser(self.session, username, password)

    def getNumberOfRegistredUsers(self, n: int) -> int:
        return self.user_repo.getNumberOfRegistredUsers(self.session,n)
    
    def sum_title_length_to_user(self, username):
        user = self.user_repo.get_by_id(self.session, username)
        if user:
            return user.sum_title_length()
        else:
            raise ValueError("User not found")

    def get_all_users(self):
        return self.user_repo.get_all(self.session)
    
class ItemService:
    def __init__(self, session, item_repo:ItemRepository):
        self.item_repo=item_repo
        self.session = session

    def create_item(self, title, prod_year):
        item = MediaItem(title,prod_year)
        self.item_repo.add(item)
        self.session.commit()

# username='ChenFryd'
# password='K2pZg9go'
# connection_string = f"mssql+pyodbc://{username}:{password}@132.72.64.124/{username}?driver=ODBC+Driver+17+for+SQL+Server"
# engine = create_engine(connection_string)
# Base.metadata.create_all(engine)
# session = sessionmaker(bind=engine)()