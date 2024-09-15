from sqlalchemy import Column
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy.orm import relationship
from src.models import Base
# Game Match Table Model
class GameMatch(Base):
    __tablename__ = 'game_match_tab'

    match_id = Column(BIGINT(unsigned=True), primary_key=True)
    round_number = Column(TINYINT(unsigned=True), nullable=False, index=True)

    match_points = relationship('MatchPoints', back_populates='game_match')
    
    __table_args__ = {'mysql_engine': 'InnoDB'}