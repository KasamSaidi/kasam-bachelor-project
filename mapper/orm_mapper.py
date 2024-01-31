from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

db_directory = "sqlite:///data.db"
Base = declarative_base()

# global user_id


def create_base(boolean):
    if boolean:
        engine = create_engine(db_directory)
        Base.metadata.create_all(engine)
        global session
        session = Session(engine)
        global user_id
        user_id = 0


def create_webapp_base(webapp_session):
    global session
    session = webapp_session


def webapp_user_session(webapp_user_id):
    global user_id
    user_id = webapp_user_id


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    def __init__(self, name: str, password: str):
        self.name = name
        self.hashed_password = password

def user_mapper(name, password):
    user_mapper.user = User(name, password)
    session.add(user_mapper.user)
    session.commit()
    session.refresh(user_mapper.user)

def stmt_results():
    result = session.execute(select(User.id, User.name, User.hashed_password))
    return result


def stmt_result_password(users_id):
    stmt = select(User.hashed_password).where(User.id == users_id)
    result = session.execute(stmt)
    return result


# def delete_session():
#     session.close()
#     engine.dispose()
