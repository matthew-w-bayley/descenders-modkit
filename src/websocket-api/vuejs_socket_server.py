import asyncio
from common.dbms import DBMS
from websocket import WebSocket
import time
import socketio
from aiohttp import web
import json
import requests
import os

DISCORD_API_URL = "https://discord.com/api/users/@me"

class VuejsSocketServer:
    def __init__(self, dbms: DBMS, web_socket: WebSocket, host='0.0.0.0', port=40000):
        self.dbms = dbms
        self.web_socket = web_socket

        self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
        self.app = web.Application()
        self.sio.attach(self.app)
        self.host = host
        self.port = port

        self.sio.event(self.connect)
        self.sio.event(self.disconnect)
        self.sio.event(self.message)
        self.sio.event(self.authenticate)

        self.identifiers = {
            'total_users_online': lambda: len(self.web_socket.players),
            'total_stored_times': self.dbms.get_total_stored_times,
            'total_replay_size': self.get_total_replay_size,
            'times_submitted_past_30_days': self.get_times_past_30_days,
            'time': self.get_time
        }
    
    async def get_time(self, time_id):
        return await self.dbms.get_time(int(time_id))

    def get_total_replay_size(self):
        # get size of ./replays
        size = 0
        with os.popen('du -s --block-size=1G ./replays') as p:
            size = p.read().split()[0]
        return size

    def verify_discord_token(self, token):
        """ Verify Discord OAuth token and return user info """
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(DISCORD_API_URL, headers=headers)

        if response.status_code == 200:
            return response.json()  # Return user data if valid
        else:
            return None

    def get_steam_id_from_discord_id(self, token):
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(DISCORD_API_URL + '/connections', headers=headers)
        if response.status_code == 200:
            connections = response.json()
            for connection in connections:
                if connection['type'] == 'steam':
                    return connection['id']

    async def authenticate(self, sid, data):
        """ Authenticate a user when they send a valid Discord token """
        print(data)
        token = json.loads(data)["token"]
        if not token:
            self.sio.emit("auth_error", {"message": "No token provided"}, room=sid)
            return
        user = self.verify_discord_token(token)
        if not user:
            await self.sio.emit("auth_error", {"message": "Invalid token"}, room=sid)
            return
        # Store the user in the session
        await self.sio.save_session(sid, {"user": user, "token": token, "steam_id": self.get_steam_id_from_discord_id(token)})        
        await self.sio.emit("message", json.dumps({"type": "send", "identifier": "steam_id", "data": self.get_steam_id_from_discord_id(token)}), room=sid)
        print(f"User {user['username']} authenticated")
        await self.sio.emit("auth_success", {"message": "Authenticated", "user": user}, room=sid)

    async def get_times_past_30_days(self):
        return await self.dbms.get_total_stored_times(timestamp=time.time()-2592000)

    async def connect(self, sid, environ):
        print('Client connected:', sid)

    async def disconnect(self, sid):
        print('Client disconnected:', sid)

    def verify_discord_auth(self, token):
        """ Verify Discord OAuth token with Discord API """
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(DISCORD_API_URL, headers=headers)

        if response.status_code == 200:
            return response.json()  # Return user data if valid
        else:
            return None

    async def message(self, sid, data):
        if data == 'get_users':
            users = [{
                "steam_id": player.info.steam_id,
                "steam_name": player.info.steam_name,
                "reputation": player.info.reputation,
                "bike_type": player.info.bike_type,
                "world_name": player.info.world_name,
                "last_trick": player.info.last_trick,
                "time_started": player.info.time_started,
                "trails": str([{
                    "trail_name": player.trails[trail].trail_name,
                    "started": player.trails[trail].timer_info.started,
                    "time_started": player.trails[trail].timer_info.time_started,
                    "times": player.trails[trail].timer_info.times,
                } for trail in player.trails]),
                "version": player.info.version,
                "spectating": player.info.spectating,
                "spectating_id": player.info.spectating_id,
            } for player in self.web_socket.players]
            await self.sio.emit('users_update', users, room=sid)
        try:
            if type(data) == str:
                data = json.loads(data)
            if data['type'] == 'get':
                ident = data['identifier']
                func = self.identifiers[ident]
                if asyncio.iscoroutinefunction(func):
                    res = await func(data['data']) if 'data' in data else await func()
                else:
                    res = func()
                await self.sio.emit('message', json.dumps({
                    'type': 'send',
                    'identifier': ident,
                    'data': res
                }), room=sid)
            elif data['type'] == 'eval':
                session = await self.sio.get_session(sid)
                user = session.get("user") if session else None
                if user is None:
                    print("SESSION NOT FOUND!")
                    return
                if user['id'] != '437237976347705346' and user['id'] != '360866829930987521': # TODO: Modularise this
                    print("USER NOT AUTHENTICATED TO DO EVAL")
                    return

                steam_id = data['data']['steam_id']
                # This is a security risk, but it's just for testing
                for player in self.web_socket.players:
                    if player.info.steam_id == steam_id:
                        await player.send(data['data']['eval'])
        except json.JSONDecodeError:
            return

    def run(self):
        web.run_app(self.app, host=self.host, port=self.port)

    async def run_async(self):
        # This is to ensure the app is running inside an asyncio loop
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        print(f'Starting server on {self.host}:{self.port}')
        await site.start()

if __name__ == '__main__':
    server = VuejsSocketServer()
    server.run()
