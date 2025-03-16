import unittest
from unittest.mock import AsyncMock
import asyncio
import time
import importlib
trail_timer = importlib.import_module('src.websocket-api.trail_timer') # because we have a dash..
TrailTimer = trail_timer.TrailTimer

# pylint: disable=missing-function-docstring, no-member, attribute-defined-outside-init, line-too-long, protected-access

class TestTrailTimer(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.network_player = AsyncMock()
        self.timer = TrailTimer("Trail 1", self.network_player)

    async def test_add_boundary(self):
        self.timer.timer_info.started = True
        self.timer.network_player.send = AsyncMock()
        await self.timer.add_boundary("boundary1")
        self.assertEqual(len(self.timer._TrailTimer__boundaries), 1)
        self.assertFalse(self.timer.timer_info.auto_verify)
        self.timer.network_player.send.assert_called_with("SPLIT_TIME|Time requires review")

    async def test_remove_boundary(self):
        self.timer._TrailTimer__boundaries = ["boundary1", "boundary2"]
        self.timer.timer_info.started = True
        self.timer.network_player.send = AsyncMock()
        await self.timer.remove_boundary("boundary1")
        self.assertEqual(len(self.timer._TrailTimer__boundaries), 1)
        self.assertTrue(self.timer.timer_info.auto_verify)

    async def test_remove_boundary_invalidates(self):
        self.timer._TrailTimer__boundaries = ["boundary1"]
        self.timer.timer_info.started = True
        self.timer.network_player.send = AsyncMock()
        await self.timer.remove_boundary("boundary1")
        self.assertEqual(len(self.timer._TrailTimer__boundaries), 0)
        self.assertFalse(self.timer.timer_info.auto_verify)
        self.timer.network_player.send.assert_called_with("SPLIT_TIME|Time requires review")

    async def test_checkpoint(self):
        self.timer.timer_info.started = True
        self.timer._TrailTimer__checkpoints = ["checkpoint1", "checkpoint2"]
        self.timer.timer_info.times = [1.0, 2.0]
        self.timer.network_player.send = AsyncMock()
        # set async functions that return [1, 2, 3, 4] and [1, 2, 4, 5]
        self.timer.network_player.dbms.get_global_best_checkpoint_times = AsyncMock(return_value=[1, 2, 3, 4])
        self.timer.network_player.dbms.get_personal_best_checkpoint_times = AsyncMock(return_value=[2, 3, 4, 5])
        await self.timer.checkpoint(5, "checkpoint3")
        self.assertEqual(len(self.timer._TrailTimer__checkpoints), 3)
        self.timer.network_player.send.assert_called_with("SPLIT_TIME|00:05.000")

    async def test_reset_boundaries(self):
        self.timer._TrailTimer__boundaries = ["boundary1", "boundary2"]
        self.timer.reset_boundaries()
        self.assertEqual(len(self.timer._TrailTimer__boundaries), 0)

    async def test_start_timer(self):
        self.timer.add_boundary("boundary1")
        self.timer.timer_info.started = False
        self.timer.invalidate_timer = AsyncMock()
        await self.timer.add_boundary("boundary1")
        await self.timer.start_timer(5)
        self.timer.timer_info.times = [1.0, 2.0, 3.0]
        self.assertEqual(self.timer.timer_info.auto_verify, True)
        self.assertEqual(self.timer.timer_info.total_checkpoints, 5)
        self.assertEqual(len(self.timer._TrailTimer__checkpoints), 0)
        self.assertEqual(self.timer.timer_info.times, [1.0, 2.0, 3.0])

    async def test_can_end_er02(self):
        self.timer._TrailTimer__boundaries = []
        self.timer.timer_info.total_checkpoints = 3
        self.timer.timer_info.times = [1.0, 2.0, 3.0]
        self.timer.timer_info.started = True
        result = await self.timer.can_end()
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERR002: Too many checkpoints")

    async def test_can_end_er03(self):
        self.timer._TrailTimer__boundaries = []
        self.timer.timer_info.total_checkpoints = 5
        self.timer.timer_info.times = [1.0, 2.0, 3.0]
        self.timer.timer_info.started = True
        result = await self.timer.can_end()
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERR003: Not enough checkpoints")

    async def test_can_end_er04(self):
        self.timer._TrailTimer__boundaries = []
        self.timer.timer_info.total_checkpoints = 5
        self.timer.timer_info.times = []
        self.timer.timer_info.started = True
        result = await self.timer.can_end()
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERR004: No times logged")

    async def test_can_end_er05(self):
        self.timer._TrailTimer__boundaries = []
        self.timer.timer_info.total_checkpoints = 5
        self.timer.timer_info.times = [-1]
        self.timer.timer_info.started = True
        result = await self.timer.can_end()
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERR005: Time is negative")
    
    async def test_can_end_er06(self):
        self.timer._TrailTimer__boundaries = []
        self.timer.timer_info.total_checkpoints = 5
        self.timer.timer_info.times = [1.0, 2.0, 3.0]
        self.timer.timer_info.started = False
        result = await self.timer.can_end()
        self.assertFalse(result[0])
        self.assertEqual(result[1], "ERR006: Timer not started")
    
    async def test_can_end_success(self):
        self.timer._TrailTimer__boundaries = []
        self.timer.timer_info.total_checkpoints = 4
        self.timer.timer_info.times = [1.0, 2.0, 3.0]
        self.timer.timer_info.started = True
        self.timer.timer_info.time_started = time.time() - 3 # time started 3 seconds ago
        result = await self.timer.can_end()
        self.assertEqual(result[1], "No errors")
        self.assertTrue(result[0])

if __name__ == '__main__':
    unittest.main()