CREATE TABLE trails (
    "trail_id" SERIAL PRIMARY KEY,
    "world_name" TEXT,
    "trail_name" TEXT,
    "version" TEXT,
    UNIQUE("world_name", "trail_name", "version")
);

CREATE TABLE bike_types (
    "bike_id" INTEGER PRIMARY KEY,
    "bike_name" TEXT
);
INSERT INTO bike_types ("bike_id", "bike_name") VALUES (0, 'enduro');
INSERT INTO bike_types ("bike_id", "bike_name") VALUES (1, 'downhill');
INSERT INTO bike_types ("bike_id", "bike_name") VALUES (2, 'hardtail');

CREATE TABLE player_times (
    "player_time_id" BIGINT, -- Unique ID for each time
    "steam_id" TEXT, -- Steam ID of the player
    "submission_timestamp" FLOAT, -- Time the time was submitted
    "trail_id" INTEGER NOT NULL, -- ID of the trail the time was set on
    "bike_id" INTEGER,
    "starting_speed" FLOAT, -- Speed the player started at
    "version" TEXT, -- modkit version used
    "game_version" TEXT, -- game version used
    "deleted" BOOLEAN, -- If the time has been deleted
    PRIMARY KEY ("player_time_id"), -- Primary key is the time ID
    FOREIGN KEY ("trail_id")
    REFERENCES trails ("trail_id")
);

CREATE TABLE verifications (
    "player_time_id" BIGINT, -- ID of the time being verified
    "verifier_id" BIGINT, -- Discord ID of the verifier
    "verification_timestamp" FLOAT, -- Time the verification was submitted
    "verified" BOOLEAN -- If the time has been verified
);

CREATE TABLE website_users (
    "discord_id" BIGINT UNIQUE,
    "steam_id" TEXT,
    "discord_name" TEXT,
    "authorised" BOOLEAN,
    PRIMARY KEY ("discord_id")
);

CREATE TABLE players (
    "steam_id" TEXT PRIMARY KEY,
    "steam_name" TEXT
);

CREATE TABLE checkpoint_times (
    "player_time_id" BIGINT NOT NULL,
    "checkpoint_num" INTEGER,
    "checkpoint_time" FLOAT,
    FOREIGN KEY ("player_time_id")
    REFERENCES player_times ("player_time_id")
    ON DELETE CASCADE
);

CREATE TABLE pending_items (
    "steam_id" TEXT,
    "item_id" TEXT,
    "time_redeemed" FLOAT,
    CONSTRAINT "fk_steam_id"
    FOREIGN KEY ("steam_id")
    REFERENCES players ("steam_id")
);

--CREATE TABLE foreign_trail_checkpoint(
--    
--)

--CREATE TABLE foreign_trail(
--
--    "map_name" TEXT,
--    "trail_name" TEXT,
--    "splits_are_checkpoints" BOOLEAN,
--
--)

CREATE MATERIALIZED VIEW all_Times AS
 WITH maxcheckpoints AS (
         SELECT DISTINCT ON (checkpoint_times_1.player_time_id) checkpoint_times_1.player_time_id,
            checkpoint_times_1.checkpoint_num AS max_checkpoint
           FROM checkpoint_times checkpoint_times_1
          ORDER BY checkpoint_times_1.player_time_id, checkpoint_times_1.checkpoint_num DESC
        )
 SELECT player_times.player_time_id,
    player_times.steam_id,
    player_times.submission_timestamp,
    player_times.trail_id,
    player_times.bike_id,
    player_times.starting_speed,
    player_times.version,
    player_times.game_version,
    player_times.deleted,
    checkpoint_times.checkpoint_time AS final_time,
    COALESCE(verifications.verified, false) AS verified,
    verifications.verifier_id
   FROM checkpoint_times
     JOIN maxcheckpoints ON checkpoint_times.player_time_id = maxcheckpoints.player_time_id AND checkpoint_times.checkpoint_num = maxcheckpoints.max_checkpoint
     JOIN player_times ON player_times.player_time_id = checkpoint_times.player_time_id
     LEFT JOIN verifications ON verifications.player_time_id = checkpoint_times.player_time_id;
