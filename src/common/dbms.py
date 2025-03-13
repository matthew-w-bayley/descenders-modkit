""" Database Management System (DBMS) for managing data using SQLAlchemy. """
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.future import select
import time
from common.dbms_models import (
    Player, PlayerTime, CheckpointTime, Trail,
    Verification, WebsiteUser, PendingItems, AllTimes
)


# Database Management System
class DBMS:
    """ A simple Database Management System (DBMS) class for managing data using SQLAlchemy. """

    def __init__(self, db_url: str):
        # check if db_url is connectable
        self.engine = create_async_engine(db_url, echo=False, pool_size=30, max_overflow=30)
        self.async_session = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def db_connected(self):
        try:
            async with self.engine.connect() as conn:
                await conn.execute(select(1))
            return True
        except Exception:
            return False

    async def get_id_from_name(self, steam_name):
        async with self.async_session() as session:
            result = await session.execute(select(Player).filter_by(steam_name=steam_name))
            player = result.scalar_one_or_none()
            return player.steam_id if player else None

    async def update_player(self, steam_id, steam_name):
        '''
        Update the player's steam name and id.
        '''
        async with self.async_session() as session:
            player = await session.get(Player, steam_id)
            if player:
                player.steam_name = steam_name
            else:
                player = Player(steam_id=steam_id, steam_name=steam_name)
                session.add(player)
            await session.commit()

    async def get_player(self, steam_id):
        async with self.async_session() as session:
            player = await session.get(Player, steam_id)
            # if player does not exist, add it and return None
            if not player:
                player = Player(steam_id=steam_id, steam_name=None)
                session.add(player)
                await session.commit()
            return player.steam_name if player else None

    async def get_all_players(self):
        async with self.async_session() as session:
            result = await session.execute(select(Player))
            return result.scalars().all()

    async def get_trail_id(self, trail_name, world_name):
        async with self.async_session() as session:
            result = await session.execute(
                select(Trail).filter_by(
                    trail_name=trail_name,
                    world_name=world_name)
                )
            trail = result.scalar_one_or_none()
            # If trail does not exist, create it
            if trail is None:
                trail = Trail(
                    trail_name=trail_name,
                    world_name=world_name
                )
                session.add(trail)
                await session.commit()
                # Return the trail id
                return await self.get_trail_id(trail_name, world_name) # recursive!
            return trail.trail_id if trail else None

    async def submit_time(
        self,
        steam_id: str,
        checkpoint_times: list[float],
        trail_name: str,
        current_world: str,
        bike_id : int,
        starting_speed: float,
        version: str,
        game_version: str,
        auto_verify: bool = True,
        deleted: bool = False
    ):
        player_time_id = hash(
            str(checkpoint_times[-1]) + str(steam_id) + str(time.time())
        ) # TODO: This hash function may have collisions
        print(player_time_id)
        await self.get_player(steam_id) # Ensure player exists
        if auto_verify:
            await self.submit_time_verification(player_time_id, 0, True)
        async with self.async_session() as session:
            new_time = PlayerTime(
                player_time_id=player_time_id,
                steam_id=steam_id,
                submission_timestamp=time.time(),
                trail_id=await self.get_trail_id(trail_name, current_world),
                bike_id=bike_id,
                starting_speed=starting_speed,
                version=version,
                game_version=game_version,
                deleted=deleted
            )
            session.add(new_time)
            await session.commit()

            for n, checkpoint_time in enumerate(checkpoint_times):
                split = CheckpointTime(
                    player_time_id=player_time_id,
                    checkpoint_num=n,
                    checkpoint_time=float(checkpoint_time),
                )
                session.add(split)

            await session.commit()
        return player_time_id

    async def get_total_stored_times(self, timestamp: int = 0) -> int:
        async with self.async_session() as session:
            result = await session.execute(
                select(AllTimes)
                .where(AllTimes.submission_timestamp > timestamp)
            )
            return len(result.scalars().all())

    async def get_trails(self, only_populated = True) -> list[Trail]:
        async with self.async_session() as session:
            query = select(Trail.trail_name, Trail.world_name)
            if only_populated:
                from sqlalchemy import and_
                query = (query.join(
                        AllTimes,
                        Trail.trail_id == AllTimes.trail_id
                    )
                    .where(and_(AllTimes.deleted.is_(False), AllTimes.verified))
                    .group_by(Trail.trail_name, Trail.world_name)
                )
            result = await session.execute(query)
            trails = result.all()
            return [
                {
                    "trail_name": trail.trail_name,
                    "world_name": trail.world_name
                }
                for trail in trails
            ]

    async def get_leaderboard(
            self,
            trail_name = None,
            world_name = None,
            num=10,
            verified=True
        ) -> list[dict]:
        async with self.async_session() as session:
            query = (
                select(AllTimes)  # Select all columns from the AllTimes model
                .distinct(AllTimes.trail_id, AllTimes.steam_id)  # group by (trail_id, steam_id)
                .filter_by(deleted=False, verified=verified) # don't include deleted times
                .order_by(  # required for DISTINCT ON to work correctly
                    AllTimes.trail_id,  # Order by trail_id first
                    AllTimes.steam_id,  # Then order by steam_id
                    AllTimes.final_time  # order by final_time for smallest final_time
                )
            )
            # if we have a trail name then discriminate to that trail
            if trail_name is not None and world_name is not None:
                query = (query
                    .join(Trail, Trail.trail_id == AllTimes.trail_id)
                    .filter(
                        Trail.trail_name == trail_name
                        and Trail.world_name == world_name
                    )
                )
            query = query.order_by(AllTimes.final_time)
            # if we want to limit then limit
            if num:
                query = query.limit(num)
            result = await session.execute(query)
            times = result.scalars().all()
            # order times by final time
            times = sorted(times, key=lambda x: x.final_time)
            return [
                {
                    "place": i + 1,
                    "starting_speed": all_times.starting_speed,
                    "name": (await self.get_player(all_times.steam_id)),
                    "bike": all_times.bike_id,
                    "version": all_times.version,
                    "verified":all_times.verified,
                    "deleted":all_times.deleted,
                    "time_id": all_times.player_time_id,
                    "time": all_times.final_time,
                    "submission_timestamp": all_times.submission_timestamp
                }
                for i, all_times in enumerate(times)
            ]
    
    async def delete_time(self, time_id):
        async with self.async_session() as session:
            time = await session.get(PlayerTime, time_id)
            time.deleted = True
            await session.commit()
    
    async def get_time(self, time_id):
        async with self.async_session() as session:
            # get from alltimes
            query = select(AllTimes).where(AllTimes.player_time_id == time_id)
            result = await session.execute(query)
            time = result.scalar_one_or_none()
            
            return {
                "starting_speed": time.starting_speed,
                "name": (await session.get(Player, time.steam_id)).steam_name,
                "bike": time.bike_id,
                "version": time.version,
                "time_id": str(time.player_time_id),
                "submission_timestamp": time.submission_timestamp,
                "time": time.final_time,
                "verified": time.verified,
                "deleted": time.deleted
            }

    async def submit_time_verification(
            self,
            time_id: int,
            verifier_id: int,
            verified: bool
        ):
        async with self.async_session() as session:
            verification = Verification(
                verifier_id=verifier_id,
                verification_timestamp=time.time(),
                verified=verified,
                player_time_id=time_id
            )
            session.add(verification)
            await session.commit()

    async def authorise_discord_user(self, discord_id):
        async with self.async_session() as session:
            user = await session.get(WebsiteUser, discord_id)
            user.authorised = True
            await session.commit()
    
    async def get_discord_user(self, discord_id):
        async with self.async_session() as session:
            user = await session.get(WebsiteUser, discord_id)
            return user
    
    async def add_discord_user(self, discord_id, steam_id, discord_name):
        async with self.async_session() as session:
            user = WebsiteUser(
                discord_id=discord_id,
                steam_id=steam_id,
                discord_name=discord_name,
                authorised=False
            )
            session.add(user)
            await session.commit()

    async def get_personal_best_checkpoint_times(self, steam_id, trail_name, world_name) -> list[float]|None:  
        pass

    async def get_global_best_checkpoint_times(self, trail_name, world_name) -> list[float]|None:
        async with self.async_session() as session:
            # get the best time for the trail
            query = (
                select(AllTimes)
                .join(Trail, Trail.trail_id == AllTimes.trail_id)
                .filter(
                    Trail.trail_name == trail_name,
                    Trail.world_name == world_name,
                    AllTimes.deleted.is_(False),
                    AllTimes.verified
                )
                .order_by(AllTimes.final_time)
                .limit(1)
            )
            # then get the checkpoint times for that time
            result = await session.execute(query)
            best_time = result.scalar_one_or_none()
            if best_time is None:
                return None
            query = (
                select(CheckpointTime.checkpoint_time)
                .filter_by(player_time_id=best_time.player_time_id)
                .order_by(CheckpointTime.checkpoint_num)
            )
            result = await session.execute(query)
            return [time for time in result.scalars().all()]

    async def get_recent_times(self, page=1, itemsPerPage=10, sortBy="submission_timestamp", sortDesc=False):
        async with self.async_session() as session:
            query = select(AllTimes)
            # TODO: This should be a dictionary
            if sortBy == "submission_timestamp":
                query = query.order_by(AllTimes.submission_timestamp.desc() if sortDesc else AllTimes.submission_timestamp)
            elif sortBy == "time":
                query = query.order_by(AllTimes.final_time.desc() if sortDesc else AllTimes.final_time)
            elif sortBy == "starting_speed":
                query = query.order_by(AllTimes.starting_speed.desc() if sortDesc else AllTimes.starting_speed)
            elif sortBy == "name":
                query = query.order_by(AllTimes.steam_id.desc() if sortDesc else AllTimes.steam_id)
            elif sortBy == "bike":
                query = query.order_by(AllTimes.bike_id.desc() if sortDesc else AllTimes.bike_id)
            elif sortBy == "version":
                query = query.order_by(AllTimes.version.desc() if sortDesc else AllTimes.version)

            if itemsPerPage != -1 and page and itemsPerPage:
                query = query.limit(itemsPerPage).offset((page - 1) * itemsPerPage)
            result = await session.execute(query)
            times = result.scalars().all()
            return [
                {
                    "starting_speed": all_times.starting_speed,
                    "name": await self.get_player(all_times.steam_id),
                    "bike": all_times.bike_id,
                    "version": all_times.version,
                    "verified":all_times.verified,
                    "deleted":all_times.deleted,
                    "time_id": str(all_times.player_time_id),
                    "time": all_times.final_time,
                    "submission_timestamp": all_times.submission_timestamp
                }
                for all_times in times
            ]

    async def get_trail_max_starting_speed(self, trail_name, world_name):
        async with self.async_session() as session:
            result = await session.execute(
                select(func.max(PlayerTime.starting_speed))
                .join(Trail, Trail.trail_id == PlayerTime.trail_id)
                .where(
                    Trail.trail_name == trail_name,
                    Trail.world_name == world_name,
                    PlayerTime.starting_speed != 0,
                    PlayerTime.deleted.is_(False),
                )
            )
            avg_speed = result.scalar_one_or_none()
            return avg_speed if avg_speed else 10000000000

    async def close(self):
        await self.engine.dispose()
    
    async def get_pending_items(self, steam_id) -> list[PendingItems]:
        async with self.async_session() as session:
            result = await session.execute(select(PendingItems).filter_by(
                steam_id=steam_id,
                time_redeemed=None
            ))
            return result.scalars().all()
    
    async def redeem_pending_item(self, steam_id, item_id):
        async with self.async_session() as session:
            pending_item = await session.get(PendingItems, (steam_id, item_id, None))
            if pending_item:
                pending_item.time_redeemed = time.time()
                await session.commit()

# Example usage:
# dbms = DBMS("postgresql+asyncpg://user:password@localhost/modkit")
# await dbms.init_db()
