"""Unit tests for Tapo DL100 extended controls, sensors, and jammed states."""

import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock

# Stub dependencies if running outside full HA environment
for mod in [
    "voluptuous",
    "homeassistant",
    "homeassistant.components",
    "homeassistant.components.lock",
    "homeassistant.components.switch",
    "homeassistant.components.number",
    "homeassistant.components.sensor",
    "homeassistant.components.binary_sensor",
    "homeassistant.config_entries",
    "homeassistant.const",
    "homeassistant.core",
    "homeassistant.exceptions",
    "homeassistant.helpers",
    "homeassistant.helpers.entity",
    "homeassistant.helpers.entity_platform",
    "homeassistant.helpers.aiohttp_client",
    "homeassistant.helpers.update_coordinator",
    "homeassistant.util",
    "Crypto",
    "Crypto.Cipher",
    "aiohttp",
]:
    sys.modules.setdefault(mod, MagicMock())

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from custom_components.tapo_dl100.api import DeviceInfo, DlklapApi


class TestExtendedControls(unittest.TestCase):
    """Test suite for extended controls, sensors, and jammed status."""

    def test_device_info_jammed_mapping(self):
        """Test is_jammed correctly identifies motor stall states (3 and 4)."""
        # Status 0 = Locked
        info_locked = DeviceInfo(lock_status=0, battery_percentage=50, at_low_battery=False, raw={})
        self.assertFalse(info_locked.is_jammed)

        # Status 1 = Unlocked
        info_unlocked = DeviceInfo(lock_status=1, battery_percentage=50, at_low_battery=False, raw={})
        self.assertFalse(info_unlocked.is_jammed)

        # Status 2 = Uncalibrated
        info_uncal = DeviceInfo(lock_status=2, battery_percentage=50, at_low_battery=False, raw={})
        self.assertFalse(info_uncal.is_jammed)

        # Status 3 = Jammed while unlocking
        info_jam_unlock = DeviceInfo(lock_status=3, battery_percentage=50, at_low_battery=False, raw={}, is_jammed=True)
        self.assertTrue(info_jam_unlock.is_jammed)

        # Status 4 = Jammed while locking
        info_jam_lock = DeviceInfo(lock_status=4, battery_percentage=50, at_low_battery=False, raw={}, is_jammed=True)
        self.assertTrue(info_jam_lock.is_jammed)

    def test_device_info_attributes(self):
        """Test extended attributes initialization."""
        info = DeviceInfo(
            lock_status=0,
            battery_percentage=51,
            at_low_battery=False,
            raw={"rssi": -55},
            is_jammed=False,
            rssi=-55,
            auto_lock_enabled=True,
            auto_lock_delay=300,
            speaker_enabled=True,
            speaker_volume=50,
            doorjam_alarm_enabled=True,
            pin_scrambling_enabled=True,
        )
        self.assertEqual(info.rssi, -55)
        self.assertTrue(info.auto_lock_enabled)
        self.assertEqual(info.auto_lock_delay, 300)
        self.assertTrue(info.speaker_enabled)
        self.assertEqual(info.speaker_volume, 50)
        self.assertTrue(info.doorjam_alarm_enabled)
        self.assertTrue(info.pin_scrambling_enabled)

    def test_parse_batched_device_info(self):
        """Test parsing of batched multipleRequest response."""
        mock_response = {
            "result": {
                "responses": [
                    {
                        "error_code": 0,
                        "result": {
                            "lock_status": 0,
                            "battery_percentage": 51,
                            "at_low_battery": False,
                            "rssi": -55,
                        },
                    },
                    {
                        "error_code": 0,
                        "result": {
                            "switch_auto_lock": True,
                            "auto_lock_time": 300,
                        },
                    },
                    {
                        "error_code": 0,
                        "result": {
                            "switch_speaker": True,
                            "volume": 50,
                        },
                    },
                    {
                        "error_code": 0,
                        "result": {
                            "switch_doorjam_alarm": True,
                        },
                    },
                    {
                        "error_code": 0,
                        "result": {
                            "switch_scrambling_mode": True,
                        },
                    },
                ]
            }
        }

        info = DlklapApi._parse_batched_info(mock_response)
        self.assertEqual(info.lock_status, 0)
        self.assertFalse(info.is_jammed)
        self.assertEqual(info.battery_percentage, 51)
        self.assertEqual(info.rssi, -55)
        self.assertTrue(info.auto_lock_enabled)
        self.assertEqual(info.auto_lock_delay, 300)
        self.assertTrue(info.speaker_enabled)
        self.assertEqual(info.speaker_volume, 50)
        self.assertTrue(info.doorjam_alarm_enabled)
        self.assertTrue(info.pin_scrambling_enabled)

    def test_parse_batched_device_info_graceful_partial_failure(self):
        """Test graceful degradation when some optional queries return errors."""
        mock_response = {
            "result": {
                "responses": [
                    {
                        "error_code": 0,
                        "result": {
                            "lock_status": 3,  # Jammed!
                            "battery_percentage": 40,
                            "at_low_battery": True,
                            "rssi": -72,
                        },
                    },
                    {"error_code": -1002, "msg": "invalid param"},
                    {"error_code": -1001, "msg": "not supported"},
                    {"error_code": 0, "result": {"switch_doorjam_alarm": False}},
                    {"error_code": 0, "result": {"switch_scrambling_mode": False}},
                ]
            }
        }

        info = DlklapApi._parse_batched_info(mock_response)
        self.assertEqual(info.lock_status, 3)
        self.assertTrue(info.is_jammed)
        self.assertEqual(info.battery_percentage, 40)
        self.assertTrue(info.at_low_battery)
        self.assertEqual(info.rssi, -72)
        # Optional failed calls fallback to None
        self.assertIsNone(info.auto_lock_enabled)
        self.assertIsNone(info.auto_lock_delay)
        self.assertIsNone(info.speaker_enabled)
        self.assertFalse(info.doorjam_alarm_enabled)
        self.assertFalse(info.pin_scrambling_enabled)


    def test_set_methods_call_structure(self):
        """Test set_* methods construct expected JSON payloads."""
        import asyncio

        api = DlklapApi(
            ip="192.168.20.55",
            cloud_username="user@example.com",
            cloud_password="password",
            lock_name="Back Door Lock",
            ssl_verify=False,
            websession=MagicMock(),
            logger=MagicMock(),
            device_id="DEV123",
            terminal_uuid="UUID123",
        )

        mock_session = MagicMock()
        mock_session.call = AsyncMock(return_value={"result": {"responses": [{"error_code": 0}]}})
        api._session = mock_session

        async def run_tests():
            # set_auto_lock
            await api.set_auto_lock(True, 180)
            mock_session.call.assert_called_with([{"method": "setAutoLockInfo", "params": {"switch_auto_lock": True, "auto_lock_time": 180}}])

            # set_speaker
            await api.set_speaker(False, 25)
            mock_session.call.assert_called_with([{"method": "setSpeaker", "params": {"switch_speaker": False, "volume": 25}}])

            # set_doorjam_alarm
            await api.set_doorjam_alarm(True)
            mock_session.call.assert_called_with([{"method": "setSwitchDoorjamAlarm", "params": {"switch_doorjam_alarm": True}}])

            # set_pin_scrambling
            await api.set_pin_scrambling(False)
            mock_session.call.assert_called_with([{"method": "setSwitchScrambling", "params": {"switch_scrambling_mode": False}}])

        asyncio.run(run_tests())


if __name__ == "__main__":
    unittest.main()
