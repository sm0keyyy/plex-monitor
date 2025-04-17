import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path to import plex_monitor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import plex_monitor

class TestPlexMonitor(unittest.TestCase):
    """Test cases for the Plex Monitor script."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock config for testing
        self.mock_config = {
            "discord_webhook_url": "https://discord.com/api/webhooks/test",
            "update_interval_seconds": 30,
            "services": {
                "plex": {
                    "url": "http://localhost:32400",
                    "token": "test_token"
                },
                "radarr": {
                    "url": "http://localhost:7878",
                    "api_key": "test_api_key"
                }
            }
        }

    @patch('plex_monitor.requests.Session')
    @patch('plex_monitor.PlexServer')
    def test_get_plex_status_online(self, mock_plex_server, mock_session):
        """Test get_plex_status when Plex is online."""
        # Set up the mock
        mock_plex = MagicMock()
        mock_sessions = [MagicMock(), MagicMock()]  # Two mock sessions
        mock_plex.sessions.return_value = mock_sessions
        mock_plex_server.return_value = mock_plex

        # Call the function
        result = plex_monitor.get_plex_status(self.mock_config["services"]["plex"])

        # Verify the result
        self.assertEqual(result["status"], "Online")
        self.assertEqual(result["sessions"], 2)
        self.assertIsNone(result["error"])

    @patch('plex_monitor.requests.Session')
    @patch('plex_monitor.PlexServer')
    def test_get_plex_status_error(self, mock_plex_server, mock_session):
        """Test get_plex_status when Plex returns an error."""
        # Set up the mock to raise an exception
        mock_plex_server.side_effect = plex_monitor.Unauthorized("Invalid token")

        # Call the function
        result = plex_monitor.get_plex_status(self.mock_config["services"]["plex"])

        # Verify the result
        self.assertEqual(result["status"], "Error")
        self.assertEqual(result["sessions"], "N/A")
        self.assertEqual(result["error"], "Unauthorized")

    @patch('plex_monitor.RadarrAPI')
    def test_get_radarr_status_online(self, mock_radarr_api):
        """Test get_radarr_status when Radarr is online."""
        # Set up the mock
        mock_radarr = MagicMock()
        mock_radarr.get_system_status.return_value = {"version": "3.0.0"}
        mock_radarr.get_queue.return_value = {"records": [{"id": 1}, {"id": 2}]}
        mock_radarr_api.return_value = mock_radarr

        # Call the function
        result = plex_monitor.get_radarr_status(self.mock_config["services"]["radarr"])

        # Verify the result
        self.assertEqual(result["status"], "Online")
        self.assertEqual(result["queue_count"], 2)
        self.assertIsNone(result["error"])

    def test_format_discord_message(self):
        """Test format_discord_message function."""
        # Create test statuses
        statuses = {
            "plex": {"status": "Online", "sessions": 2, "error": None},
            "radarr": {"status": "Online", "queue_count": 3, "error": None},
            "sonarr": {"status": "Error", "queue_count": "N/A", "error": "Connection failed"}
        }

        # Call the function
        result = plex_monitor.format_discord_message(statuses)

        # Verify the result
        self.assertIn("embeds", result)
        self.assertEqual(len(result["embeds"]), 1)
        
        # Check embed fields
        fields = result["embeds"][0]["fields"]
        self.assertEqual(len(fields), 4)  # 3 services + 1 blank field for even layout
        
        # Check Plex field
        plex_field = next(field for field in fields if "Plex" in field["name"])
        self.assertIn("Sessions: 2", plex_field["value"])
        
        # Check Radarr field
        radarr_field = next(field for field in fields if "Radarr" in field["name"])
        self.assertIn("Queue: 3", radarr_field["value"])
        
        # Check Sonarr field (error state)
        sonarr_field = next(field for field in fields if "Sonarr" in field["name"])
        self.assertIn("Error: Connection failed", sonarr_field["value"])

if __name__ == '__main__':
    unittest.main()
