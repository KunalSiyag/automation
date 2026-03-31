import pytest
from monitor import APIMonitor

@pytest.fixture
def monitor():
    return APIMonitor()

def test_add_endpoint(monitor):
    monitor.add_endpoint('Test', 'https://example.com')
    assert len(monitor.endpoints) == 1
    assert monitor.endpoints[0]['name'] == 'Test'

def test_check_endpoint(monitor):
    endpoint = {'name': 'Google', 'url': 'https://www.google.com', 'method': 'GET'}
    result = monitor.check_endpoint(endpoint)
    assert 'status' in result
    assert 'response_time' in result

def test_get_stats(monitor):
    monitor.results = [
        {'healthy': True, 'response_time': 100},
        {'healthy': True, 'response_time': 200},
        {'healthy': False, 'response_time': 0}
    ]
    stats = monitor.get_stats()
    assert stats['total_checks'] == 3
    assert stats['healthy'] == 2
    assert stats['uptime_percentage'] == pytest.approx(66.66, 0.1)
