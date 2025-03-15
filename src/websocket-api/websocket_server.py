""" Used to host the socket server. """
from typing import Union
import time
import asyncio
from asyncio import StreamReader, StreamWriter
import logging
from websocket import WebSocket
from common.dbms import DBMS

class PlayerNotFound(Exception):
    """ Exception called when the descenders unity client could not be found """

class DisconnectError(Exception):
    """ Exception called when the descenders unity client disconnects """

class WebSocketServer():
    """ Used to communicate quickly with the Descenders Unity client. """
    def __init__(self, ip: str, port: int, dbms: DBMS):
        self.host = ip
        self.port = port
        self.dbms = dbms
        self.timeout = 120
        self.read_buffer_size = 100
        self.website_socket_server = None
        self.players: list[WebSocket] = []

    def delete_player(self, player: WebSocket):
        """ Deletes the player from the socket server """
        if player not in self.players:
            return # player already deleted
        self.players.remove(player)
        player.writer.close()
        del player

    async def check_lifes(self):
        """ Checks if the players are still alive """
        while True:
            for player in self.players:
                if not player.alive:
                    self.delete_player(player)
            await asyncio.sleep(1)

    async def handle_client(self, reader: StreamReader, writer: StreamWriter):
        """ Creates a client from their socket and address """        
        address = writer.get_extra_info('peername')
        player = WebSocket(address, self, reader, writer)
        print(f"Player {player} connected")
        self.players.append(player)
        await player.send("SUCCESS")
        try:
            while player.alive:
                # Read the data from the client
                try:
                    data = await asyncio.wait_for(
                        reader.readuntil(b'\n'),
                        timeout=self.timeout
                    )
                except asyncio.LimitOverrunError:
                    data = await asyncio.wait_for(
                        reader.read(self.read_buffer_size),
                        timeout=self.timeout
                    )
                # If no data is received, then the client has disconnected
                if not data:
                    raise DisconnectError("Client disconnected")
                message = data.decode()
                # If message does not end with a newline character, then read more data
                while not message.endswith("\n"):
                    data = await asyncio.wait_for(
                        reader.read(self.read_buffer_size),
                        timeout=self.timeout
                    )
                    message += data.decode()
                # Remove the newline character from the message
                message = message.rstrip("\n")
                # if the message is a heartbeat, then ignore it
                if message == "HEARTBEAT|":
                    continue
                # Handle UPLOAD_REPLAY operation
                if message.startswith("UPLOAD_REPLAY|"):
                    _, time_id, base64_replay = message.split("|", 2)
                    await player.upload_replay(time_id, base64_replay)
                else:
                    asyncio.create_task(player.handle_data(message))
        except (asyncio.TimeoutError, ConnectionResetError, BrokenPipeError, DisconnectError):
            print(f"Player {player} disconnected")
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except ConnectionResetError:
                pass
            self.delete_player(player)
