"""
File Converter - Convert between different file formats
Supports: JSON, CSV, YAML, XML
"""

import json
import csv
import sys
from pathlib import Path

class FileConverter:
    def __init__(self):
        self.supported_formats = ['json', 'csv', 'yaml', 'xml']
    
    def detect_format(self, filename):
        return Path(filename).suffix[1:].lower()
    
    def read_json(self, filename):
        with open(filename, 'r') as f:
            return json.load(f)
    
    def write_json(self, data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def read_csv(self, filename):
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def write_csv(self, data, filename):
        if not data:
            return
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    
    def convert(self, input_file, output_file):
        input_format = self.detect_format(input_file)
        output_format = self.detect_format(output_file)
        
        if input_format not in self.supported_formats:
            raise ValueError(f"Unsupported input format: {input_format}")
        if output_format not in self.supported_formats:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        # Read data
        if input_format == 'json':
            data = self.read_json(input_file)
        elif input_format == 'csv':
            data = self.read_csv(input_file)
        else:
            raise NotImplementedError(f"Reading {input_format} not yet implemented")
        
        # Write data
        if output_format == 'json':
            self.write_json(data, output_file)
        elif output_format == 'csv':
            self.write_csv(data, output_file)
        else:
            raise NotImplementedError(f"Writing {output_format} not yet implemented")
        
        print(f"✅ Converted {input_file} to {output_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python converter.py <input_file> <output_file>")
        sys.exit(1)
    
    converter = FileConverter()
    converter.convert(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
