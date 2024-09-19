from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy.orm import relationship
from src.models import Base

class User(Base):
    """
    User Table Model using SQLAlchemy ORM
    """
    __tablename__ = 'user_tab'

    user_id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_name = Column(String(50), nullable=False, index=True, unique=True)
    hashed_password = Column(String(60), nullable=False) # bcrypt password will be 60 characters long always
    user_role = Column(Enum('player', 'manager', 'admin'), nullable=False)
    team_id = Column(TINYINT(unsigned=True), ForeignKey('team_tab.team_id', ondelete='CASCADE'), nullable=True) # Foreign Key for player and managers

    team = relationship('Team', back_populates='users')

    __table_args__ = {'mysql_engine': 'InnoDB'}