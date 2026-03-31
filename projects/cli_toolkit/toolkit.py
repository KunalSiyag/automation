"""
CLI Toolkit - Collection of useful command-line utilities
"""

import os
import sys
import hashlib
import json
from pathlib import Path

class CLIToolkit:
    def __init__(self):
        self.commands = {
            'hash': self.hash_file,
            'count': self.count_lines,
            'search': self.search_text,
            'size': self.directory_size,
            'info': self.file_info
        }
    
    def hash_file(self, filename: str, algorithm: str = 'sha256') -> str:
        hash_obj = hashlib.new(algorithm)
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    
    def count_lines(self, filename: str) -> dict:
        with open(filename, 'r') as f:
            lines = f.readlines()
        return {
            'total_lines': len(lines),
            'non_empty_lines': sum(1 for line in lines if line.strip()),
            'empty_lines': sum(1 for line in lines if not line.strip())
        }
    
    def search_text(self, directory: str, pattern: str) -> list:
        results = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.txt') or file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r') as f:
                            for i, line in enumerate(f, 1):
                                if pattern in line:
                                    results.append({
                                        'file': filepath,
                                        'line': i,
                                        'content': line.strip()
                                    })
                    except:
                        pass
        return results
    
    def directory_size(self, directory: str) -> dict:
        total_size = 0
        file_count = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
                    file_count += 1
        return {
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'file_count': file_count
        }
    
    def file_info(self, filename: str) -> dict:
        stat = os.stat(filename)
        return {
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'is_file': os.path.isfile(filename),
            'is_dir': os.path.isdir(filename),
            'extension': Path(filename).suffix
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python toolkit.py <command> [args]")
        print("Commands: hash, count, search, size, info")
        return
    
    toolkit = CLIToolkit()
    command = sys.argv[1]
    
    if command in toolkit.commands:
        result = toolkit.commands[command](*sys.argv[2:])
        print(json.dumps(result, indent=2))
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    main()
