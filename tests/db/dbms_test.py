'''
Module to test DBMS

Note: A database must be running on localhost:5432 with the following credentials:
    database = "postgres"
    user = postgres
    password = postgres
    host = localhost
    port = 5432

The schema is automatically reset before each test, so the database must be empty.

To run the tests, run the following command:
    python -m unittest tests.dbms_test

Start database with:
    cd server/src/database-schema/
    docker-compose up -d
'''
import unittest
import time
from src.common.dbms import DBMS

class TestDbms(unittest.IsolatedAsyncioTestCase):

    def connect(self):
        import psycopg2
        conn = psycopg2.connect(
            database = "postgres", 
            user = "postgres", 
            host= 'localhost',
            password = "postgres",
            port = 5432
        )
        return conn

    def reset_database(self):
        drop_all = "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(drop_all)
        with open('./src/db/schema.sql') as f:
            schema = f.read()
            cur.execute(schema)
        conn.commit()
        conn.close()

    async def get_dbms_instance(self):
        self.reset_database()
        dbms_instance = DBMS("postgresql+asyncpg://postgres:postgres@localhost/postgres")
        return dbms_instance

    async def test_update_player(self):
        dbms_instance = await self.get_dbms_instance()
        await dbms_instance.update_player("76561198000000000", "test_player")
        # check if player was added
        self.assertEqual(await dbms_instance.get_player("76561198000000000"), "test_player")
    
    async def test_update_player_with_existing_player(self):
        dbms_instance = await self.get_dbms_instance()
        await dbms_instance.update_player("76561198000000000", "test_player")
        await dbms_instance.update_player("76561198000000000", "test_player2")
        # check if player was updated in dbms.py
        self.assertEqual(await dbms_instance.get_player("76561198000000000"), "test_player2")
        # check if player was updated in the database
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM players WHERE steam_id = '76561198000000000'")
        result = cur.fetchone()
        conn.close()
        self.assertEqual(result[1], "test_player2")

    async def test_update_player_with_existing_player_and_no_name(self):
        dbms_instance = await self.get_dbms_instance()
        await dbms_instance.update_player("76561198000000000", "test_player")
        await dbms_instance.update_player("76561198000000000", "")
        # check if player was updated
        self.assertEqual(await dbms_instance.get_player("76561198000000000"), "")

    async def test_submit_time(self):
        dbms_instance = await self.get_dbms_instance()
        await dbms_instance.submit_time(
            "76561198000000000", # steam_id
            [1, 2, 3, 4], # checkpoint_times
            "Test Trail", # trail_name
            "Test World", # world_name
            1, # bike_type_id
            8.34, # starting_speed
            "1.34", # version
            "", # game version
        )
        # check if time was added
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM player_times WHERE steam_id = '76561198000000000'")
        result = cur.fetchone()
        conn.close()
        self.assertEqual(result[1], "76561198000000000")
    
    async def test_submit_time_multiple(self):
        # test submitting multiple times at once
        dbms_instance = await self.get_dbms_instance()
        for i in range(0, 400):
            await dbms_instance.submit_time(
                "76561198000000000", # steam_id
                [1, 2, 3, 4], # checkpoint_times
                "Test Trail", # trail_name
                "Test World", # world_name
                1, # bike_type_id
                8.34, # starting_speed
                "1.34", # version
                "", # game version
            )
        # check if times were added
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM player_times WHERE steam_id = '76561198000000000'")
        result = cur.fetchone()
        conn.close()
        self.assertEqual(result[0], 400)

    async def test_get_trails_empty(self):
        dbms_instance = await self.get_dbms_instance()
        trails = await dbms_instance.get_trails()
        self.assertEqual(trails, [])

    async def test_get_trails_generated_by_submit_time(self):
        dbms_instance = await self.get_dbms_instance()
        trails = await dbms_instance.get_trails()
        self.assertEqual(trails, [])
        # add trail
        await dbms_instance.submit_time(
            "76561198000000000", # steam_id
            [1, 2, 3, 4], # checkpoint_times
            "Test Trail", # trail_name
            "Test World", # world_name
            1, # bike_type_id
            8.34, # starting_speed
            "1.34", # version
            "", # game version
        )
        trails = await dbms_instance.get_trails()
        self.assertEqual(trails, [{'trail_name': 'Test Trail', 'world_name': 'Test World'}])

    async def test_get_trails_generated_by_get_trail_id(self):
        dbms_instance = await self.get_dbms_instance()
        trails = await dbms_instance.get_trails()
        self.assertEqual(trails, [])
        # add trail
        await dbms_instance.get_trail_id("Test Trail", "Test World")
        trails = await dbms_instance.get_trails()
        self.assertEqual(trails, [{'trail_name': 'Test Trail', 'world_name': 'Test World'}])

    async def test_get_id_from_name(self):
        dbms_instance = await self.get_dbms_instance()
        await dbms_instance.update_player("76561198000000000", "test_player")
        self.assertEqual(await dbms_instance.get_id_from_name("test_player"), "76561198000000000")

    async def test_get_player(self):
        dbms_instance = await self.get_dbms_instance()
        await dbms_instance.update_player("76561198000000000", "test_player")
        self.assertEqual(await dbms_instance.get_player("76561198000000000"), "test_player")

    async def test_get_player_from_empty(self):
        dbms_instance = await self.get_dbms_instance()
        self.assertEqual(await dbms_instance.get_player("76561198000000000"), None)

    async def test_get_player_from_empty_with_empty_id(self):
        dbms_instance = await self.get_dbms_instance()
        self.assertEqual(await dbms_instance.get_player(""), None)

    async def test_get_all_players(self):
        dbms_instance = await self.get_dbms_instance()
        await dbms_instance.update_player("76561198000000000", "test_player")
        await dbms_instance.update_player("76561198000000001", "test_player2")
        self.assertEqual(len(await dbms_instance.get_all_players()), 2)
        self.assertEqual([player.steam_name for player in await dbms_instance.get_all_players()], ["test_player", "test_player2"])

    
    async def test_get_leaderboard(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000000', 'test_player')")
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (1, '76561198000000000', 0, 1, 8.34, '1.34', 0, FALSE)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 1, 0)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 2, 1)")
        cur.execute("INSERT INTO verifications (player_time_id, verified) VALUES (1, TRUE)")
        conn.commit()
        leaderboard = await dbms_instance.get_leaderboard("Test Trail", "Test World")
        self.assertEqual(leaderboard, [
            {
                "place": 1,
                "starting_speed": 8.34,
                "name": "test_player",
                "bike": 1,
                "version": "1.34",
                "verified": True,
                "deleted": False,
                "time_id": 1,
                "time": 1,
                "submission_timestamp": 0,
            }
        ])
    
    async def test_delete_time(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000000', 'test_player')")
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (1, '76561198000000000', 0, 1, 8.34, '1.34', 0, FALSE)")
        conn.commit()
        await dbms_instance.delete_time(1)
        cur.execute("SELECT deleted FROM player_times WHERE player_time_id = 1")
        result = cur.fetchone()
        self.assertEqual(result[0], True)
    
    async def test_submit_time_verification(self):
        dbms_instance = await self.get_dbms_instance()
        await dbms_instance.submit_time_verification(1, 1, True)
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT verified FROM verifications WHERE player_time_id = 1")
        result = cur.fetchone()
        self.assertEqual(result[0], True)

    async def test_leaderboard_with_unverified_time(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000000', 'test_player')")
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (1, '76561198000000000', 0, 1, 8.34, '1.34', 0, FALSE)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 1, 0)")
        conn.commit()
        leaderboard = await dbms_instance.get_leaderboard("Test Trail", "Test World")
        self.assertEqual(leaderboard, [])

    async def test_leaderboard_with_verified_time(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000000', 'test_player')")
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (1, '76561198000000000', 0, 1, 8.34, '1.34', 0, FALSE)")
        cur.execute("INSERT INTO verifications (player_time_id, verified) VALUES (1, TRUE)")
        # insert checkpoint times
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 1, 0)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 2, 1)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 3, 4)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 4, 9)")
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000022', 'test_player2')")
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (2, '76561198000000022', 0, 1, 8.34, '1.34', 0, FALSE)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (2, 1, 0)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (2, 2, 1)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (2, 3, 4)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (2, 4, 7)")
        cur.execute("INSERT INTO verifications (player_time_id, verified) VALUES (2, TRUE)")
        conn.commit()
        leaderboard = await dbms_instance.get_leaderboard("Test Trail", "Test World")
        self.assertEqual(leaderboard, [
            {
                "place": 1,
                "starting_speed": 8.34,
                "name": "test_player2",
                "bike": 1,
                "version": "1.34",
                "verified": True,
                "time_id": 2,
                "time": 7,
                "submission_timestamp": 0,
                "deleted": False,
            },
            {
                "place": 2,
                "starting_speed": 8.34,
                "name": "test_player",
                "bike": 1,
                "version": "1.34",
                "verified": True,
                "time_id": 1,
                "time": 9,
                "submission_timestamp": 0,
                "deleted": False,
            }
        ])

    async def test_leaderboard_with_deleted_time(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000000', 'test_player')")
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (1, '76561198000000000', 0, 1, 8.34, '1.34', 0, TRUE)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 1, 0)")
        conn.commit()
        leaderboard = await dbms_instance.get_leaderboard("Test Trail", "Test World")
        self.assertEqual(leaderboard, [])

    async def test_leaderboard_with_multiple_times(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000000', 'test_player')")
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (1, '76561198000000000', 0, 1, 8.34, '1.34', 0, FALSE)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 1, 1)")
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (2, '76561198000000000', 0, 1, 8.34, '1.34', 1, FALSE)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (2, 1, 2)")
        cur.execute("INSERT INTO verifications (player_time_id, verified) VALUES (1, TRUE)")
        cur.execute("INSERT INTO verifications (player_time_id, verified) VALUES (2, TRUE)")
        conn.commit()
        leaderboard = await dbms_instance.get_leaderboard("Test Trail", "Test World")
        # only returns one because the other is the same id
        self.assertEqual(len(leaderboard), 1)
        self.assertEqual(leaderboard, [
            {
                "place": 1,
                "starting_speed": 8.34,
                "name": "test_player",
                "bike": 1,
                "version": "1.34",
                "verified": True,
                "time_id": 1,
                "time": 1,
                "submission_timestamp": 0,
                "deleted": False,
            }
        ])
    
    async def test_add_discord_user(self):
        dbms_instance = await self.get_dbms_instance()
        await dbms_instance.add_discord_user(123456789, "76561198000000000", "test_discord")
        self.assertEqual((await dbms_instance.get_discord_user(123456789)).discord_name, "test_discord")
    
    async def test_authorise_discord_user(self):
        dbms_instance = await self.get_dbms_instance()
        await dbms_instance.add_discord_user(123456789, "76561198000000000", "test_discord")
        await dbms_instance.authorise_discord_user(123456789)
        self.assertEqual((await dbms_instance.get_discord_user(123456789)).steam_id, "76561198000000000")
        self.assertEqual((await dbms_instance.get_discord_user(123456789)).authorised, True)

    @unittest.skip("not yet implemented")
    async def test_get_personal_best_checkpoint_times(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000000', 'test_player')")
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (1, '76561198000000000', 0, 1, 8.34, '1.34', 0, FALSE)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 1, 1)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 2, 2)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 3, 3)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 4, 4)")
        conn.commit()
        personal_best_checkpoint_times = await dbms_instance.get_personal_best_checkpoint_times("Test Trail", "Test World", "76561198000000000")
        self.assertEqual(personal_best_checkpoint_times, [1, 2, 3, 4])
    
    @unittest.skip("not yet implemented")
    async def test_get_personal_best_checkpoint_times_with_multiple_times(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000000', 'test_player')")
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (1, '76561198000000000', 0, 1, 8.34, '1.34', 0, FALSE)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 1, 1)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 2, 2)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 3, 3)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 4, 4)")
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (2, '76561198000000000', 0, 1, 8.34, '1.34', 1, FALSE)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (2, 1, 1)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (2, 2, 2)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (2, 3, 3)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (2, 4, 5)")
        conn.commit()
        personal_best_checkpoint_times = await dbms_instance.get_personal_best_checkpoint_times("Test Trail", "Test World", "76561198000000000")
        self.assertEqual(personal_best_checkpoint_times, [1, 2, 3, 4])
    
    @unittest.skip("not yet implemented")
    async def test_get_personal_best_checkpoint_times_with_unverified_time(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000000', 'test_player')")
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (1, '76561198000000000', 0, 1, 8.34, '1.34', 0, FALSE)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 1, 1)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 2, 2)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 3, 3)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 4, 4)")
        cur.execute("INSERT INTO verifications (player_time_id, verified) VALUES (1, FALSE)")
        conn.commit()
        personal_best_checkpoint_times = await dbms_instance.get_personal_best_checkpoint_times("Test Trail", "Test World", "76561198000000000")
        self.assertEqual(personal_best_checkpoint_times, [])
    
    @unittest.skip("not yet implemented")
    async def test_get_personal_best_checkpoint_times_with_deleted_time(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000000', 'test_player')")
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (1, '76561198000000000', 0, 1, 8.34, '1.34', 0, TRUE)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 1, 1)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 2, 2)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 3, 3)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 4, 4)")
        conn.commit()
        personal_best_checkpoint_times = await dbms_instance.get_personal_best_checkpoint_times("Test Trail", "Test World", "76561198000000000")
        self.assertEqual(personal_best_checkpoint_times, [])
    
    @unittest.skip("not yet implemented")
    async def test_get_global_best_checkpoint_times(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        # insert trail
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        # insert player
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000000', 'test_player')")
        # insert time
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (1, '76561198000000000', 0, 1, 8.34, '1.34', 0, FALSE)")
        # insert checkpoint times
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 1, 1)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 2, 2)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 3, 3)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 4, 4)")
        # insert verification
        cur.execute("INSERT INTO verifications (player_time_id, verified) VALUES (1, TRUE)")
        conn.commit()
        global_best_checkpoint_times = await dbms_instance.get_global_best_checkpoint_times("Test Trail", "Test World")
        self.assertEqual(global_best_checkpoint_times, [1, 2, 3, 4])
    
    @unittest.skip("not yet implemented")
    async def test_get_global_best_checkpoint_times_with_multiple_times(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        # insert trail
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        # insert player
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000000', 'test_player')")
        # insert time
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (1, '76561198000000000', 0, 1, 8.34, '1.34', 0, FALSE)")
        # insert checkpoint times
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 1, 1)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 2, 2)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 3, 3)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 4, 4)")
        # insert verification
        cur.execute("INSERT INTO verifications (player_time_id, verified) VALUES (1, TRUE)")
        # insert player
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000001', 'test_player2')")
        # insert time
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (2, '76561198000000001', 0, 1, 8.34, '1.34', 0, FALSE)")
        # insert checkpoint times
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (2, 1, 1)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (2, 2, 2)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (2, 3, 3)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (2, 4, 5)")
        # insert verification
        cur.execute("INSERT INTO verifications (player_time_id, verified) VALUES (2, TRUE)")
        conn.commit()
        global_best_checkpoint_times = await dbms_instance.get_global_best_checkpoint_times("Test Trail", "Test World")
        self.assertEqual(global_best_checkpoint_times, [1, 2, 3, 4])
    
    async def test_get_recent_times(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        # insert trail
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        # insert player
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000000', 'test_player')")
        # insert time
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (1, '76561198000000000', 0, 1, 8.34, '1.34', 0, FALSE)")
        cur.execute("INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (1, 1, 0)")
        # insert verification
        cur.execute("INSERT INTO verifications (player_time_id, verified) VALUES (1, TRUE)")
        conn.commit()
        recent_times = await dbms_instance.get_recent_times()
        self.assertEqual(recent_times, [
            {
                "starting_speed": 8.34,
                "name": "test_player",
                "bike": 1,
                "version": "1.34",
                "verified": True,
                "time_id": 1,
                "time": 0,
                "submission_timestamp": 0,
                "deleted": False,
            }
        ])
    
    async def test_get_recent_times_pagination(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        # insert trail
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        # insert player
        
        for i in range(0, 20):
            cur.execute(f"INSERT INTO players (steam_id, steam_name) VALUES ('{i}', 'test_player')")
            # insert time
            cur.execute(f"INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES ({i}, '{i}', 0, 1, 8.34, '1.34', {i}, FALSE)")
            cur.execute(f"INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES ({i}, 1, 1)")
            # insert verification
            cur.execute(f"INSERT INTO verifications (player_time_id, verified) VALUES ({i}, TRUE)")
        conn.commit()
        recent_times = await dbms_instance.get_recent_times(1)
        self.assertEqual(len(recent_times), 10)
        self.assertEqual(recent_times[0]["submission_timestamp"], 0)
        self.assertEqual(recent_times[9]["submission_timestamp"], 9)
        recent_times = await dbms_instance.get_recent_times(2)
        self.assertEqual(len(recent_times), 10)
        recent_times = await dbms_instance.get_recent_times(3)
        self.assertEqual(len(recent_times), 0)

    async def test_get_recent_times_sort_by_time(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        # insert trail
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        # insert player
        
        for i in range(0, 20):
            cur.execute(f"INSERT INTO players (steam_id, steam_name) VALUES ('{i}', 'test_player')")
            # insert time
            cur.execute(f"INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES ({i}, '{i}', 0, 1, 8.34, '1.34', {i}, FALSE)")
            cur.execute(f"INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES ({i}, 1, {i})")
            # insert verification
            cur.execute(f"INSERT INTO verifications (player_time_id, verified) VALUES ({i}, TRUE)")
        conn.commit()
        recent_times = await dbms_instance.get_recent_times(1, 10, "submission_timestamp", False)

        self.assertEqual(recent_times[0]["submission_timestamp"], 0)
        self.assertEqual(recent_times[9]["submission_timestamp"], 9)
        recent_times = await dbms_instance.get_recent_times(1, 10, "submission_timestamp", True)
        self.assertEqual(recent_times[0]["submission_timestamp"], 19)
        self.assertEqual(recent_times[9]["submission_timestamp"], 10)

    async def test_get_trail_average_starting_speed(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        # insert trail
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        # insert player
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000000', 'test_player')")
        # insert time
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (1, '76561198000000000', 0, 1, 8.34, '1.34', 0, FALSE)")
        # insert verification
        cur.execute("INSERT INTO verifications (player_time_id, verified) VALUES (1, TRUE)")
        conn.commit()
        trail_average_starting_speed = await dbms_instance.get_trail_average_starting_speed("Test Trail", "Test World")
        self.assertEqual(trail_average_starting_speed, 8.34)
    
    async def test_get_trail_average_starting_speed_with_multiple_times(self):
        dbms_instance = await self.get_dbms_instance()
        # manually insert because submit_time uses time.time() which is not deterministic
        conn = self.connect()
        cur = conn.cursor()
        # insert trail
        cur.execute("INSERT INTO trails (trail_id, trail_name, world_name) VALUES (0, 'Test Trail', 'Test World')")
        # insert player
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000000', 'test_player')")
        # insert time
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (1, '76561198000000000', 0, 1, 8.34, '1.34', 0, FALSE)")
        # insert verification
        cur.execute("INSERT INTO verifications (player_time_id, verified) VALUES (1, TRUE)")
        # insert player
        cur.execute("INSERT INTO players (steam_id, steam_name) VALUES ('76561198000000001', 'test_player2')")
        # insert time
        cur.execute("INSERT INTO player_times (player_time_id, steam_id, trail_id, bike_id, starting_speed, version, submission_timestamp, deleted) VALUES (2, '76561198000000001', 0, 1, 8.34, '1.34', 0, FALSE)")
        # insert verification
        cur.execute("INSERT INTO verifications (player_time_id, verified) VALUES (2, TRUE)")
        conn.commit()
        trail_average_starting_speed = await dbms_instance.get_trail_average_starting_speed("Test Trail", "Test World")
        self.assertEqual(trail_average_starting_speed, 8.34)