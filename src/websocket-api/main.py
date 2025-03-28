import socket
import asyncio
import os
from websocket_server import WebSocketServer
from vuejs_socket_server import VuejsSocketServer
from common.dbms import DBMS

# Constants for configuration
IP = "0.0.0.0"
SOCKET = 65433
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

"""Initialize all the components for the server."""

print("Starting websocket api", flush=True)

async def start():
    # Database Management System
    dbms_url = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

    unity_socket_server = WebSocketServer(IP, SOCKET, DBMS(dbms_url))
    vuejs_socket_server = VuejsSocketServer(DBMS(dbms_url), unity_socket_server)

    async def start_tcp_server():
        server = await asyncio.start_server(
            unity_socket_server.handle_client,
            unity_socket_server.host,
            unity_socket_server.port
        )
        print("Serving on", server.sockets[0].getsockname())
        # also run in background unity_socket_server.check_lifes()
        asyncio.create_task(unity_socket_server.check_lifes())
        asyncio.create_task(unity_socket_server.send_riders_gate())
        await server.serve_forever()

    await vuejs_socket_server.run_async()
    await start_tcp_server()


asyncio.run(start())
