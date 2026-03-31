import pytest
import json
import csv
import os
from converter import FileConverter

@pytest.fixture
def converter():
    return FileConverter()

@pytest.fixture
def sample_json_file(tmp_path):
    data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
    file_path = tmp_path / "test.json"
    with open(file_path, 'w') as f:
        json.dump(data, f)
    return file_path

def test_detect_format(converter):
    assert converter.detect_format("data.json") == "json"
    assert converter.detect_format("data.csv") == "csv"

def test_json_to_csv(converter, sample_json_file, tmp_path):
    output = tmp_path / "output.csv"
    converter.convert(str(sample_json_file), str(output))
    assert output.exists()

def test_read_json(converter, sample_json_file):
    data = converter.read_json(str(sample_json_file))
    assert len(data) == 2
    assert data[0]['name'] == 'Alice'
