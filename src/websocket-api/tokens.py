""" Tokens for descenders-modkit """
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Tokens for descenders-modkit
STEAM_API_KEY = os.getenv("STEAM_API_KEY", "")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
OAUTH2_CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID", "")
OAUTH2_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET", "")
TWITCH_TOKEN = os.getenv("TWITCH_TOKEN", "")
CERTIFICATE_CRT = os.getenv("CERTIFICATE_CRT", "")
PRIVATE_KEY_KEY = os.getenv("PRIVATE_KEY_KEY", "")
modkit_status_webhook_url = os.getenv("modkit_status_webhook_url", "")

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

if POSTGRES_DB == "":
    print("NO TOKENS FOUND!!")