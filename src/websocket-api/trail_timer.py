""" Used to track the time on a map """
from typing import TYPE_CHECKING
import dataclasses
import time
import requests
import logging
import asyncio
import os
import nest_asyncio # Used to fix RuntimeError in using async from thread
from twitch_chat_irc import twitch_chat_irc
from tokens import TWITCH_TOKEN, DISCORD_WEBHOOK
nest_asyncio.apply()

if TYPE_CHECKING: # for imports with intellisense
    from websocket import WebSocket

@dataclasses.dataclass
class TimerInfo:
    """ Information for the functionality of a timer """
    started: bool # Whether the timer has started
    auto_verify: bool # whether the time should be verified when finished
    times: list[float] # List of times
    starting_speed: float # The starting speed of the player
    total_checkpoints: int # The total number of checkpoints in the trail
    time_started: float # The time the timer was started

class TrailTimer():
    """ Used to track the time on a trail """
    def __init__(self, trail_name, network_player):
        self.trail_name = trail_name
        self.network_player : WebSocket = network_player
        self.timer_info = TimerInfo(
            started=False, auto_verify=True, times=[], starting_speed=0,
            total_checkpoints=0, time_started=0
        )
        self.__boundaries = []
        self.__checkpoints = []

    def __str__(self):
        return f"Trail {self.trail_name} for player {self.network_player.info.steam_name} in boundary_num={len(self.__boundaries)},starting_speed={self.timer_info.starting_speed},times={self.timer_info.times}"

    __repr__  = __str__ # so dict/list serialisation uses __str__

    async def add_boundary(self, boundary_guid):
        """
        Add a boundary to the list of boundaries encountered during a run.

        If the list of boundard a run has started, it sets the 'auto_verify' flag to
        False and sends a message to the network player indicating that their time will be reviewed
        due to cuts.
        """
        # if we were out of bounds and are in a run
        if len(self.__boundaries) == 0 and self.timer_info.started:
            # note we cannot verify this user instantly
            if self.timer_info.auto_verify:
                await self.network_player.send("SPLIT_TIME|Time requires review")
            self.timer_info.auto_verify = False
        if boundary_guid not in self.__boundaries:
            self.__boundaries.append(boundary_guid)

    async def remove_boundary(self, boundary_guid):
        """
        Remove a boundary from the list of boundaries encountered during a run.
        """
        if boundary_guid in self.__boundaries:
            self.__boundaries.remove(boundary_guid)
        if len(self.__boundaries) == 0:
            if self.timer_info.started:
                # note we cannot verify this user instantly
                if self.timer_info.auto_verify:
                    await self.network_player.send("SPLIT_TIME|Time requires review")
                self.timer_info.auto_verify = False

    def reset_boundaries(self):
        """
        Reset the list of boundaries encountered during a run.
        """
        self.__boundaries = []

    async def start_timer(self, total_checkpoints: int):
        """ Start the timer. """
        logging.info(
            "%s '%s'\t- started timer with checkpoints %s", self.network_player.info.steam_id,
            self.network_player.info.steam_name, total_checkpoints
        )
        self.__checkpoints = [] # reset the checkpoints
        self.timer_info.auto_verify = True
        self.timer_info.starting_speed = 0
        if len(self.__boundaries) == 0:
            if self.timer_info.auto_verify:
                await self.network_player.send("SPLIT_TIME|Time requires review")
            self.timer_info.auto_verify = False
                
        self.timer_info.started = True
        self.timer_info.total_checkpoints = total_checkpoints
        self.timer_info.time_started = time.time()
        self.timer_info.times = []

    async def checkpoint(self, client_time: float, checkpoint_hash: str):
        """Log a checkpoint."""
        steam_id = self.network_player.info.steam_id
        steam_name = self.network_player.info.steam_name

        logging.info(
            "%s '%s'\t- entered checkpoint with client time %s",
            steam_id, steam_name, client_time
        )

        if self.timer_info.started and checkpoint_hash not in self.__checkpoints:
            self.__checkpoints.append(checkpoint_hash)
            self.timer_info.times.append(float(client_time))

            wr = await self.network_player.dbms.get_global_best_checkpoint_times(
                self.trail_name,
                self.network_player.info.world_name
            )
            pb = await self.network_player.dbms.get_personal_best_checkpoint_times(
                self.trail_name,
                self.network_player.info.world_name,
                self.network_player.info.steam_id
            )

            total_checkpoints = self.timer_info.total_checkpoints - 1
            index = len(self.timer_info.times) - 1
            if wr is not None and total_checkpoints == len(wr):
                wr_diff = wr[index] - float(client_time)
            else:
                wr_diff = None

            if pb is not None and total_checkpoints == len(pb):
                pb_diff = pb[index] - float(client_time)
            else:
                pb_diff = None

            mess = self.calculate_split_message(wr_diff, pb_diff, client_time)
            await self.network_player.send(f"SPLIT_TIME|{mess}")

    def calculate_split_message(self, time_diff: float, time_diff_local: float, client_time: float) -> str:
        """Calculate split time message."""
        mess = ""

        if time_diff is None:
            pass
        elif time_diff > 0:
            mess += f"<color=lime>-{round(abs(time_diff), 3)}</color> WR"
        elif time_diff == 0:
            mess += f"<color=orange>+{round(abs(time_diff), 3)}</color> WR"
        elif time_diff < 0:
            mess += f"<color=red>+{round(abs(time_diff), 3)}</color> WR"

        if time_diff_local is None:
            pass
        elif time_diff_local > 0:
            mess += f"  <color=lime>-{round(abs(time_diff_local), 3)}</color> PB"
        elif time_diff_local == 0:
            mess += f"  <color=orange>+{round(abs(time_diff_local), 3)}</color> PB"
        elif time_diff_local < 0:
            mess += f"  <color=red>+{round(abs(time_diff_local), 3)}</color> PB"

        if not mess:
            mess = self.secs_to_str(float(client_time))

        return mess


    async def invalidate_timer(self, reason: str, always=False):
        """ Invalidate the timer. """
        logging.info(
            "%s '%s'\t- invalidated due to %s, always=%s",
            self.network_player.info.steam_id, self.network_player.info.steam_name, reason, always
        )
        if (not self.timer_info.started) and not always:
            return
        await self.network_player.send(f"INVALIDATE_TIME|{reason}\\n")
        self.timer_info.started = False

    async def can_end(self) -> tuple[bool, str]:
        """ Check if the data is valid to be able to end the timer """
        errors = {
            "ERR006: Timer not started":
                lambda: not self.timer_info.started,
            "ERR004: No times logged":
                lambda: len(self.timer_info.times) == 0,
            "ERR005: Time is negative":
                lambda: self.timer_info.times[len(self.timer_info.times)-1] < 0,
            "ERR002: Too many checkpoints":
                lambda: len(self.timer_info.times) > self.timer_info.total_checkpoints-1,
            "ERR003: Not enough checkpoints":
                lambda: len(self.timer_info.times) < self.timer_info.total_checkpoints-1,
            "ERR007: Client time did not match server time":
                lambda: not(
                    (
                        (
                            (time.time() - self.timer_info.time_started)
                            - self.timer_info.times[len(self.timer_info.times)-1]
                        ) < 1
                    and (
                        (time.time() - self.timer_info.time_started)
                        - self.timer_info.times[len(self.timer_info.times)-1]
                        ) > -1
                    )
                )
        }
        for error_message, error in errors.items():
            if error():
                return (False, error_message)
        return (True, "No errors")

    async def request_replay(self, time_id, retries=3):
        """ Request the replay from the client. """
        # send the replay request to the client
        await self.network_player.send(f"UPLOAD_REPLAY|{time_id}")
        # check if the replay was uploaded
        await asyncio.sleep(20)
        # ./replays/{time_id}.replay
        replay_path = f"./replays/{time_id}.replay"
        if not os.path.exists(replay_path) and retries > 0:
            # if the replay was not uploaded, we need to request the replay again
            await self.request_replay(time_id, retries - 1)
        elif not os.path.exists(replay_path):
            # if the replay was not uploaded after retries, invalidate the timer
            await self.invalidate_timer("Replay not uploaded after multiple attempts")

    async def end_timer(self, client_time: float):
        """ End the timer. """
        self.timer_info.times.append(float(client_time)) # add the final time
        can_end = await self.can_end()
        # reset the timer
        was_started = self.timer_info.started
        self.timer_info.started = False
        # submit the time to the database
        time_id = None
        try:
            time_id = await self.network_player.dbms.submit_time(
                self.network_player.info.steam_id,
                self.timer_info.times,
                self.trail_name,
                self.network_player.info.world_name,
                self.network_player.info.bike_id,
                self.timer_info.starting_speed,
                self.network_player.info.version,
                "",
                self.timer_info.auto_verify and can_end[0],
                deleted=not can_end[0]
            )
        except Exception as e:
            # this is a critical error - need to log and notify the user
            print("FATAL ERROR: Failed to submit time to database!", flush=True)
            print("FATAL ERROR: ", e, flush=True)
            await self.network_player.send_popup(
                    "Criticial Error",
                    (
                        "The server has encountered a critical error and was "
                        f"unable to submit your time. Client time: {client_time}"
                    )
            )

        # ask client to upload replay
        asyncio.create_task(self.request_replay(time_id))
        # if the timer has not started, return
        # this is to prevent the timer from ending multiple times, but retain
        # all times in the database. Important for live racing
        if not was_started:
            return
        # send the submitted time to the client
        comment = "verified" if self.timer_info.auto_verify else "requires review"
        secs_str = TrailTimer.secs_to_str(client_time)
        # if time being spectated
        async def twitch_notif():
            try:
                # if the player is being spectated
                if self.network_player.info.steam_id in [network_player.info.spectating_id for network_player in self.network_player.parent.players]:
                    connection = twitch_chat_irc.TwitchChatIRC('nohumanman', TWITCH_TOKEN)
                    connection.send("bbb171", f"{secs_str} 🚴‍♂️💨") # change to send to self.network_player.info.twitch_channel
                    # this should serve as a log of times
                    time_url = f"https://modkit.nohumanman.com/time/{time_id}"
                    connection.send("bbb171", f"{time_url}")
                    # send to discord webhook
                    data = {
                        "content": f"[{secs_str}]({time_url}) by {self.network_player.info.steam_name} 🚴‍♂️💨",
                        "username": "Descenders Modkit"
                    }
                    requests.post(DISCORD_WEBHOOK, json = data)
            except Exception as e:
                logging.error(f"Failed to send message to twitch chat: {e}")
        asyncio.create_task(twitch_notif())

        if not can_end[0]:
            await self.network_player.send_popup("Time Invalid",
                    (
                        f"Time cannot be verified due to the following reason: {can_end[1]}."
                        " You cannot ask us to verify this run."
                    )
            )
        elif not self.timer_info.auto_verify:
            await self.network_player.send_popup("Verification Required",
                    (
                        f"Your time of {secs_str} can be verified if it is a legal run with no cuts."
                        " You can ask for verification in the #request-verification"
                        " channel on the Descenders Competitive Discord server."
                        f" Please only do this if you know your run is valid. ID{time_id}"
                    )
            )

        if can_end[0]:
            await self.network_player.send(
                f"TIMER_FINISH|{secs_str}\\n{comment}"
            )
        else:
            await self.network_player.send(
                f"TIMER_FINISH|{secs_str}\\n{can_end[1]}\\nLive Racers: This time is still logged!\\n"
            )
        
        # update the leaderboards and medals on connected clients
        async def update():
            await self.update_leaderboards()
        asyncio.create_task(update())
        self.timer_info.auto_verify = True

    async def potential_cheat(self, client_time: float):
        """ Called when the client time does not match the server time. """
        logging.info(
            "%s '%s'\t- potentially cheated! client time %s", self.network_player.info.steam_id,
            self.network_player.info.steam_name, client_time
        )
        await self.invalidate_timer("Client time did not match server time!")

    async def update_leaderboards(self):
        """ Update the leaderboards for the trail. """
        for net_player in self.network_player.parent.players:
            await net_player.send(
                "LEADERBOARD|"
                + self.trail_name + "|"
                + str(
                    await self.network_player.get_leaderboard(self.trail_name)
                )
            )

    @staticmethod
    def secs_to_str(secs):
        """ Convert seconds to a string. """
        secs = float(secs)
        d_mins = int(secs // 60)
        d_secs = int(secs % 60)
        fraction = float(secs * 1000)
        fraction = round(fraction % 1000)
        if fraction == 1000:
            fraction = 0
            d_secs += 1
        if len(str(d_mins)) == 1:
            d_mins = "0" + str(d_mins)
        if len(str(d_secs)) == 1:
            d_secs = "0" + str(d_secs)
        while len(str(fraction)) < 3:
            fraction = "0" + str(fraction)
        return f"{d_mins}:{d_secs}.{fraction}"

    @staticmethod
    def ord(n):
        """ Convert a number to an ordinal. """
        return (
            str(n)
            + ("th" if 4 <= (n % 100) <= 20 else {
                1: "st",
                2: "nd",
                3: "rd"
            }.get(n % 10, "th")
            )
        )
