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
    hashed_password = Column(String(72), nullable=False) # bcrypt hashed password, max length 72
    user_role = Column(Enum('viewer', 'player', 'manager', 'admin'), nullable=False)
    team_id = Column(TINYINT(unsigned=True), ForeignKey('team_tab.team_id'), nullable=True) # Foreign Key

    team = relationship('Team', back_populates='users')

    __table_args__ = {'mysql_engine': 'InnoDB'}