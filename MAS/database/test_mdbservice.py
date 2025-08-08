"""
Unit Tests for the MongoDB Service connection, data inserting and retrieval.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from dtos import UserProfile, Profile
from mdbservice import *

class TestMDBService(unittest.TestCase):

    @patch("mdbservice.MongoClient")
    def setUp(self, mock_client):
        # Setup mock database structure
        self.mock_client = MagicMock()
        mock_client.return_value = self.mock_client
        self.mock_db = self.mock_client.__getitem__.return_value
        self.mock_profiles = self.mock_db.__getitem__.return_value
        self.mock_sessions = self.mock_db.__getitem__.return_value

        # Mock list_indexes return value
        self.mock_sessions.list_indexes.return_value = [
	    {"key": {"_id": 1}},
            {"key": {"session_id": 1}},
            {"key": {"mode": 1}},
            {"key": {"start_time": 1}},
            {"key": {"agent_sequence": 1}},
            {"key": {"inserted_at": 1}},
        ]

        self.service = MDBService(uri="mongodb://fake-uri")
        self.service._sessions = self.mock_sessions
        self.service._profiles = self.mock_profiles

    def test_insert_session_success(self):
        self.service.insert_session({"session_id": "123", "mode": "demo", "start_time": "2025-01-01T00:00:00", "agent_sequence": []})
        self.mock_sessions.insert_one.assert_called_once()

    def test_insert_session_missing_key(self):
        with self.assertRaises(MissingIndexException):
            self.service.insert_session({"session_id": "123", "mode": "demo"})

    def test_get_latest_session(self):
        self.service.get_latest_session()
        self.mock_sessions.find_one.assert_called_once()

    def test_get_session_by_id(self):
        self.service.get_session_by_id("abc")
        self.mock_sessions.find_one.assert_called_with({"session_id": "abc"})

    def test_get_sessions_by_mode(self):
        self.service.get_sessions_by_mode("demo")
        self.mock_sessions.find_one.assert_called()

    def test_ping_success(self):
        self.service._client.admin.command.return_value = {"ok": 1}
        self.service.ping()
        self.service._client.admin.command.assert_called_once_with("ping")


if __name__ == '__main__':
    unittest.main()
