import pytest
from monitor import APIMonitor
import requests # Needed for mocking
from unittest.mock import patch, MagicMock

@pytest.fixture
def monitor():
    return APIMonitor()

def test_add_endpoint(monitor):
    monitor.add_endpoint('Test', 'https://example.com')
    assert len(monitor.endpoints) == 1
    assert monitor.endpoints[0]['name'] == 'Test'

def test_check_endpoint_success(monitor):
    # Mock requests.request to simulate a successful response
    with patch('requests.request') as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None # No HTTP error
        mock_request.return_value = mock_response

        endpoint = {'name': 'Google', 'url': 'https://www.google.com', 'method': 'GET'}
        result = monitor.check_endpoint(endpoint)

        assert result['healthy'] is True
        assert result['status_code'] == 200
        assert 'response_time' in result and result['response_time'] >= 0 # Time depends on mock execution, just ensure it's there
        assert result['error_message'] is None
        mock_request.assert_called_once()

def test_check_endpoint_failure_invalid_url(monitor):
    # Mock requests.request to simulate a ConnectionError
    with patch('requests.request', side_effect=requests.exceptions.ConnectionError("DNS lookup failed")) as mock_request:
        endpoint = {'name': 'Invalid', 'url': 'http://definitely.not.a.real.domain', 'timeout': 1}
        result = monitor.check_endpoint(endpoint)

        assert result['healthy'] is False
        assert result['status_code'] is None
        assert 'response_time' in result and result['response_time'] >= 0
        assert result['error_message'] is not None
        assert "Connection error" in result['error_message']
        mock_request.assert_called_once()

def test_check_endpoint_failure_timeout(monitor):
    # Mock requests.request to simulate a Timeout
    with patch('requests.request', side_effect=requests.exceptions.Timeout("Request timed out")) as mock_request:
        endpoint = {'name': 'Timeout', 'url': 'https://httpbin.org/delay/3', 'timeout': 1}
        result = monitor.check_endpoint(endpoint)

        assert result['healthy'] is False
        assert result['status_code'] is None
        assert 'response_time' in result and result['response_time'] >= 0
        assert result['error_message'] is not None
        assert "Timeout after 1 seconds." in result['error_message'] # Specific message from our code
        mock_request.assert_called_once()

def test_check_endpoint_failure_http_error(monitor):
    # Mock requests.request to simulate an HTTPError (e.g., 404)
    with patch('requests.request') as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.reason = "NOT FOUND"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_request.return_value = mock_response

        endpoint = {'name': 'HTTP Error', 'url': 'https://httpbin.org/status/404', 'timeout': 5}
        result = monitor.check_endpoint(endpoint)

        assert result['healthy'] is False
        assert result['status_code'] == 404
        assert 'response_time' in result and result['response_time'] >= 0
        assert result['error_message'] is not None
        assert "HTTP error: 404 NOT FOUND" in result['error_message']
        mock_request.assert_called_once()

def test_get_stats(monitor):
    monitor.results = [
        {'healthy': True, 'response_time': 100, 'status_code': 200, 'error_message': None},
        {'healthy': True, 'response_time': 200, 'status_code': 200, 'error_message': None},
        {'healthy': False, 'response_time': 50, 'status_code': None, 'error_message': "Connection error"}
    ]
    stats = monitor.get_stats()
    assert stats['total_checks'] == 3
    assert stats['healthy'] == 2
    assert stats['unhealthy'] == 1
    assert stats['uptime_percentage'] == pytest.approx(66.67, 0.01)
    assert stats['avg_response_time_ms'] == 150 # (100+200)/2
