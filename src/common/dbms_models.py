""" Database Models for the modkit Database """
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, BigInteger, TIMESTAMP

Base = declarative_base()

# Database Models
class Player(Base):
    __tablename__ = 'players'

    steam_id = Column(String, primary_key=True)
    steam_name = Column(String)

class BikeType(Base):
    __tablename__ = 'bike_types'

    bike_id = Column(Integer, primary_key=True)
    bike_name = Column(String)

class PlayerTime(Base):
    __tablename__ = 'player_times'

    player_time_id = Column(BigInteger, primary_key=True)
    steam_id = Column(String, ForeignKey('players.steam_id'))
    submission_timestamp = Column(Float)
    trail_id = Column(Integer, ForeignKey('trails.trail_id'))
    bike_id = Column(Integer)#, ForeignKey(BikeType.bike_id))
    starting_speed = Column(Float)
    version = Column(String)
    game_version = Column(String)
    deleted = Column(Boolean)

class CheckpointTime(Base):
    __tablename__ = 'checkpoint_times'

    player_time_id = Column(BigInteger, ForeignKey('player_times.player_time_id'), primary_key=True)
    checkpoint_num = Column(Integer, primary_key=True)
    checkpoint_time = Column(Float)


class Trail(Base):
    __tablename__ = 'trails'

    trail_id = Column(Integer, primary_key=True)
    trail_name = Column(String)
    world_name = Column(String)
    version = Column(String)

class Verification(Base):
    __tablename__ = 'verifications'

    player_time_id = Column(BigInteger, primary_key=True)
    verifier_id = Column(BigInteger)
    verification_timestamp = Column(Float)
    verified = Column(Boolean)

class WebsiteUser(Base):
    __tablename__ = 'website_users'

    discord_id = Column(BigInteger, primary_key=True)
    steam_id = Column(String)
    discord_name = Column(String)
    authorised = Column(Boolean)

class AllTimes(Base):
    __tablename__ = 'all_times'
    
    player_time_id = Column(BigInteger, primary_key=True)
    steam_id = Column(String, nullable=False)
    submission_timestamp = Column(TIMESTAMP, nullable=False)
    trail_id = Column(Integer, nullable=False)
    bike_id = Column(Integer, nullable=False)
    starting_speed = Column(Float, nullable=False)
    version = Column(String, nullable=False)
    game_version = Column(String, nullable=False)
    deleted = Column(Boolean, nullable=False)
    final_time = Column(Float, nullable=False)
    verified = Column(Boolean, nullable=False, default=False)
    verifier_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)  # Adjust ForeignKey table if necessary

class PendingItems(Base):
    __tablename__ = 'pending_items'

    steam_id = Column(String, ForeignKey('players.steam_id'), primary_key=True)
    item_id = Column(String, primary_key=True)
    time_redeemed = Column(Float, primary_key=True)
