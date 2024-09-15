from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy.orm import relationship
from src.models import Base

# Match Points Table Model
class MatchPoints(Base):
    __tablename__ = 'match_points_tab'

    match_id = Column(BIGINT(unsigned=True), ForeignKey('game_match_tab.match_id', ondelete='CASCADE'), primary_key=True)
    team_id = Column(TINYINT(unsigned=True), ForeignKey('team_tab.team_id'), primary_key=True)
    goals_scored = Column(TINYINT(unsigned=True), nullable=False)

    game_match = relationship('GameMatch', back_populates='match_points')
    team = relationship('Team', back_populates='match_points')

    __table_args__ = {'mysql_engine': 'InnoDB'}
