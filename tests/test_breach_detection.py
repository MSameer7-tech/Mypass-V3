from unittest.mock import patch, Mock

import pytest
import requests

from services.breach_detection import BreachDetectionService, BreachStatus


class TestBreachDetectionService:
    def setup_method(self):
        self.service = BreachDetectionService()
        self.password = "password123"
        # SHA1 for password123 is CBFDAC6008F9CAB4083784CBD1874F76618D2A97
        # Prefix is CBFDA, Suffix is C6008F9CAB4083784CBD1874F76618D2A97

    @patch("services.breach_detection.requests.get")
    def test_empty_password_is_safe(self, mock_get):
        result = self.service.check_password("")
        assert not result.breached
        assert result.status == BreachStatus.SAFE
        mock_get.assert_not_called()

    @patch("services.breach_detection.requests.get")
    def test_password_found_in_breach(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        # Simulating HIBP API response format
        mock_response.text = "00000000000000000000000000000000000:10\r\nC6008F9CAB4083784CBD1874F76618D2A97:12345\r\nFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:1"
        mock_get.return_value = mock_response

        result = self.service.check_password(self.password)
        
        assert result.breached is True
        assert result.breach_count == 12345
        assert result.status == BreachStatus.BREACHED
        assert not result.cached
        mock_get.assert_called_once()

    @patch("services.breach_detection.requests.get")
    def test_password_not_found_in_breach(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "00000000000000000000000000000000000:10\r\nFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:1"
        mock_get.return_value = mock_response

        result = self.service.check_password(self.password)
        
        assert result.breached is False
        assert result.breach_count == 0
        assert result.status == BreachStatus.SAFE
        assert not result.cached
        mock_get.assert_called_once()

    @patch("services.breach_detection.requests.get")
    def test_caching_mechanism(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "C6008F9CAB4083784CBD1874F76618D2A97:12345"
        mock_get.return_value = mock_response

        result1 = self.service.check_password(self.password)
        assert not result1.cached
        
        result2 = self.service.check_password(self.password)
        assert result2.cached is True
        assert result2.breached is True
        assert result2.breach_count == 12345
        
        # Ensure requests.get was only called once
        mock_get.assert_called_once()

    @patch("services.breach_detection.requests.get")
    def test_rate_limiting_429(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response

        result = self.service.check_password(self.password)
        
        assert result.breached is False
        assert result.status == BreachStatus.ERROR

    @patch("services.breach_detection.requests.get")
    def test_network_offline(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError()

        result = self.service.check_password(self.password)
        
        assert result.breached is False
        assert result.status == BreachStatus.OFFLINE
