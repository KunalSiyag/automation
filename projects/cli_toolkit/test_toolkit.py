import pytest
import os
import tempfile
from toolkit import CLIToolkit

@pytest.fixture
def toolkit():
    return CLIToolkit()

@pytest.fixture
def temp_file():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("line 1\nline 2\n\nline 4\n")
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)

def test_hash_file(toolkit, temp_file):
    hash_result = toolkit.hash_file(temp_file)
    assert len(hash_result) == 64  # SHA256 length

def test_count_lines(toolkit, temp_file):
    result = toolkit.count_lines(temp_file)
    assert result['total_lines'] == 4
    assert result['non_empty_lines'] == 3
    assert result['empty_lines'] == 1

def test_file_info(toolkit, temp_file):
    info = toolkit.file_info(temp_file)
    assert info['is_file'] == True
    assert info['size'] > 0
