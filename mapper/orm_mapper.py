from datetime import datetime

from sqlalchemy import Column, Integer, String, select, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
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
    else:
        engine = create_engine(db_directory)
        Base.metadata.create_all(engine)

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

    points = relationship("Point", back_populates="user")
    badges = relationship("Badge", back_populates="user")

    def __init__(self, name: str, password: str):
        self.name = name
        self.hashed_password = password

class Point(Base):
    __tablename__ = 'points'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    points = Column(Integer)
    timestamp = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="points")

class Badge(Base):
    __tablename__ = 'badges'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    badge_name = Column(String)
    timestamp = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="badges")

def user_mapper(name, password):
    user_mapper.user = User(name, password)
    session.add(user_mapper.user)
    session.commit()
    session.refresh(user_mapper.user)

def get_total_points(username):
    user = session.query(User).filter_by(name=username).first()
    if user:
        total_points = session.query(Point).filter_by(user_id=user.id).first()
        session.refresh(user)
        return total_points.points
    return 0

def get_user_badges(username):
    user = session.query(User).filter_by(name=username).first()
    if user:
        user_badges = [badge.badge_name for badge in user.badges]
        session.refresh(user)
        return user_badges
    return []

def add_points(username, points):
    user = session.query(User).filter_by(name=username).first()
    if user:
        new_point = Point(user=user, points=points, timestamp=datetime.now())
        session.add(new_point)
        session.commit()
        session.refresh(user)
        return True
    return False

def add_badge(username, badge_name):
    user = session.query(User).filter_by(name=username).first()
    if user:
        new_badge = Badge(user=user, badge_name=badge_name, timestamp=datetime.now())
        session.add(new_badge)
        session.commit()
        session.refresh(user)
        return True
    return False

def change_user_points(username, points_change):
    user = session.query(User).filter_by(name=username).first()
    if user:
        user_points = session.query(Point).filter_by(user_id=user.id).first()
        if user_points:
            user_points.points += points_change
        else:
            new_point = Point(user=user, points=points_change, timestamp=datetime.now())
            session.add(new_point)
        session.commit()
    session.refresh(user)

def add_user_badge(username, badge_name):
    user = session.query(User).filter_by(name=username).first()
    if user:
        new_badge = Badge(user=user, badge_name=badge_name, timestamp=datetime.now())
        session.add(new_badge)
        session.commit()
    session.refresh(user)

def remove_user_badge(username, badge_name):
    user = session.query(User).filter_by(name=username).first()
    if user:
        badge_to_remove = session.query(Badge).filter_by(user_id=user.id, badge_name=badge_name).first()
        if badge_to_remove:
            session.delete(badge_to_remove)
            session.commit()
    session.refresh(user)

def stmt_results():
    result = session.execute(select(User.id, User.name, User.hashed_password))
    return result

def stmt_result_password(users_id):
    stmt = select(User.hashed_password).where(User.id == users_id)
    result = session.execute(stmt)
    return result
