"""
Tests for data analyzer.
"""

import pytest
import json
import csv
import tempfile
import os
from analyzer import DataLoader, DataAnalyzer


@pytest.fixture
def sample_data():
    """Create sample data."""
    return [
        {"name": "Alice", "age": 30, "score": 95.5},
        {"name": "Bob", "age": 25, "score": 87.3},
        {"name": "Charlie", "age": 35, "score": 92.1},
    ]


@pytest.fixture
def temp_json_file(sample_data):
    """Create temporary JSON file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def temp_csv_file(sample_data):
    """Create temporary CSV file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'age', 'score'])
        writer.writeheader()
        writer.writerows(sample_data)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


def test_data_loader_load_json(temp_json_file):
    """Test loading JSON file."""
    loader = DataLoader()
    assert loader.load_json(temp_json_file)
    assert len(loader.get_data()) == 3
    assert loader.get_columns() == ['name', 'age', 'score']


def test_data_loader_load_csv(temp_csv_file):
    """Test loading CSV file."""
    loader = DataLoader()
    assert loader.load_csv(temp_csv_file)
    assert len(loader.get_data()) == 3


def test_data_loader_shape(temp_json_file):
    """Test getting data shape."""
    loader = DataLoader()
    loader.load_json(temp_json_file)
    shape = loader.get_shape()
    assert shape == (3, 3)


def test_data_loader_get_column_data(temp_json_file):
    """Test getting column data."""
    loader = DataLoader()
    loader.load_json(temp_json_file)
    names = loader.get_column_data('name')
    assert names == ['Alice', 'Bob', 'Charlie']


def test_data_loader_filter(temp_json_file):
    """Test filtering data."""
    loader = DataLoader()
    loader.load_json(temp_json_file)
    filtered = loader.filter_data('name', 'Alice')
    assert len(filtered) == 1
    assert filtered[0]['age'] == 30


def test_data_loader_head(temp_json_file):
    """Test head method."""
    loader = DataLoader()
    loader.load_json(temp_json_file)
    head_data = loader.head(2)
    assert len(head_data) == 2
    assert head_data[0]['name'] == 'Alice'


def test_data_loader_tail(temp_json_file):
    """Test tail method."""
    loader = DataLoader()
    loader.load_json(temp_json_file)
    tail_data = loader.tail(1)
    assert len(tail_data) == 1
    assert tail_data[0]['name'] == 'Charlie'


def test_data_analyzer_numeric_columns(sample_data):
    """Test identifying numeric columns."""
    numeric_cols = DataAnalyzer.get_numeric_columns(sample_data, ['name', 'age', 'score'])
    assert set(numeric_cols) == {'age', 'score'}


def test_data_analyzer_summary_stats(sample_data):
    """Test summary statistics."""
    ages = [30, 25, 35]
    stats = DataAnalyzer.get_summary_stats(ages)
    assert stats['count'] == 3
    assert stats['min'] == 25
    assert stats['max'] == 35
    assert stats['mean'] == 30.0


def test_data_analyzer_value_counts():
    """Test value counts."""
    values = ['a', 'b', 'a', 'c', 'b', 'a']
    counts = DataAnalyzer.get_value_counts(values)
    assert counts == {'a': 3, 'b': 2, 'c': 1}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
