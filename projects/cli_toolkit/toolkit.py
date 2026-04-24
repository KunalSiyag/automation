import hashlib
import os

class CLIToolkit:
    def hash_file(self, filename: str, algorithm: str = 'sha256') -> str:
        """
        Calculates the hash of a given file.

        Args:
            filename: The path to the file.
            algorithm: The hashing algorithm to use (e.g., 'sha256', 'md5').
                       Defaults to 'sha256'.

        Returns:
            The hexadecimal hash value of the file.

        Raises:
            ValueError: If an unsupported hashing algorithm is specified.
            IOError: If the file cannot be opened or read.
        """
        hash_func = getattr(hashlib, algorithm, None)
        if hash_func is None:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

        hasher = hash_func()
        try:
            with open(filename, 'rb') as f:
                while True:
                    chunk = f.read(4096)  # Read in 4KB chunks
                    if not chunk:
                        break
                    hasher.update(chunk)
            return hasher.hexdigest()
        except FileNotFoundError:
            raise IOError(f"File not found: {filename}")
        except PermissionError:
            raise IOError(f"Permission denied to read file: {filename}")
        except Exception as e:
            raise IOError(f"Error reading file {filename}: {e}")

    def file_info(self, path: str) -> dict:
        """
        Retrieves information about a file or directory.

        Args:
            path: The path to the file or directory.

        Returns:
            A dictionary containing various pieces of information,
            such as existence, type, size, and modification times.
        """
        info = {
            'path': path,
            'exists': os.path.exists(path),
            'is_file': os.path.isfile(path),
            'is_dir': os.path.isdir(path),
            'size': 0,
            'created_at': None,
            'modified_at': None,
            'last_access_at': None,
        }

        if info['exists']:
            stat_info = os.stat(path)
            info['size'] = stat_info.st_size
            info['created_at'] = stat_info.st_ctime # Creation time (platform dependent)
            info['modified_at'] = stat_info.st_mtime # Last modification time
            info['last_access_at'] = stat_info.st_atime # Last access time

        return info

    def count_lines(self, filepath: str) -> dict:
        """
        Counts total, non-empty, and empty lines in a text file.

        Args:
            filepath: The path to the text file.

        Returns:
            A dictionary with 'total_lines', 'non_empty_lines', and 'empty_lines'.

        Raises:
            IOError: If the file cannot be opened or read.
        """
        total_lines = 0
        non_empty_lines = 0
        empty_lines = 0

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    total_lines += 1
                    if line.strip():  # Check if line is not empty after stripping whitespace
                        non_empty_lines += 1
                    else:
                        empty_lines += 1
            return {
                'total_lines': total_lines,
                'non_empty_lines': non_empty_lines,
                'empty_lines': empty_lines
            }
        except FileNotFoundError:
            raise IOError(f"File not found: {filepath}")
        except PermissionError:
            raise IOError(f"Permission denied to read file: {filepath}")
        except UnicodeDecodeError:
            raise IOError(f"Cannot decode file as UTF-8: {filepath}. It might be a binary file or in a different encoding.")
        except Exception as e:
            raise IOError(f"Error reading file {filepath}: {e}")
