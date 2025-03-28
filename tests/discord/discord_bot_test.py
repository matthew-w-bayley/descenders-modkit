import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/common/')))

import unittest
from unittest.mock import AsyncMock, patch
from discord.ext import commands
from discord_bot import DiscordBot
from discord_bot import posh_time

class TestDiscordBot(unittest.TestCase):
    @unittest.skip("Not implemented")
    @patch('discord.ext.commands.Bot.get_channel')
    def test_send_message_to_channel(self, mock_get_channel):
        # Create a mock channel to be of type discord.TextChannel
        mock_channel = AsyncMock()
        mock_get_channel.return_value = mock_channel

        # Initialize the bot
        bot = DiscordBot(discord_token='dummy_token', command_prefix='!', socket_server=None, dbms=None)

        # Run the coroutine
        message = "Test message"
        channel_id = 123456789
        bot.loop.run_until_complete(bot.send_message_to_channel(message, channel_id))

        # overwrite self.get_channel to return an instance of discord.TextChannel
        mock_get_channel.return_value = mock_channel

        # Check if get_channel was called with the correct channel_id
        mock_get_channel.assert_called_with(channel_id)

        # Check if send was called on the mock channel with the correct message
        mock_channel.send.assert_awaited_with(message)

    def test_posh_time(self):
        # Test for 0 seconds
        self.assertEqual(posh_time(0), "0 days, 0h, 0m, 0s")

        # Test for 1 second
        self.assertEqual(posh_time(1), "0 days, 0h, 0m, 1s")

        # Test for 60 seconds
        self.assertEqual(posh_time(60), "0 days, 0h, 1m, 0s")

        # Test for 3600 seconds
        self.assertEqual(posh_time(3600), "0 days, 1h, 0m, 0s")

        # Test for 86400 seconds
        self.assertEqual(posh_time(86400), "1 days, 0h, 0m, 0s")

        # Test for 90061 seconds
        self.assertEqual(posh_time(90061), "1 days, 1h, 1m, 1s")

        # Test for 172800 seconds
        self.assertEqual(posh_time(172800), "2 days, 0h, 0m, 0s")

if __name__ == '__main__':
    unittest.main()