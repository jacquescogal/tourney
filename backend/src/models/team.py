from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy.orm import relationship
from src.models import Base

# Team Table Model
class Team(Base):
    __tablename__ = 'team_tab'

    team_id = Column(TINYINT(unsigned=True), primary_key=True, autoincrement=True)
    team_name = Column(String(50), nullable=False, index=True)
    registration_date_unix = Column(BIGINT(unsigned=True), nullable=False)
    group_number = Column(TINYINT(unsigned=True), nullable=False)

    users = relationship('User', back_populates='team')
    match_points = relationship('MatchPoints', back_populates='team')

    __table_args__ = {'mysql_engine': 'InnoDB'}