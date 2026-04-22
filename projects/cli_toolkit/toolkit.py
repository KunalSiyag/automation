import hashlib
import os
import time

class CLIToolkit:
    """
    A collection of utility methods for file operations.
    """

    def hash_file(self, filename: str, algorithm: str = 'sha256') -> str:
        """
        Calculates the hash of a given file.

        Args:
            filename (str): The path to the file.
            algorithm (str): The hashing algorithm to use (e.g., 'sha256', 'md5').

        Returns:
            str: The hexadecimal hash value of the file.

        Raises:
            ValueError: If the specified algorithm is not supported.
            FileNotFoundError: If the file does not exist.
            IOError: If there's an issue reading the file.
        """
        algorithm = algorithm.lower()
        if algorithm not in hashlib.algorithms_available:
            raise ValueError(f"Unsupported hashing algorithm: {algorithm}. Available: {', '.join(hashlib.algorithms_available)}")

        try:
            hasher = hashlib.new(algorithm)
            with open(filename, 'rb') as f:
                while chunk := f.read(8192):  # Read file in chunks to handle large files
                    hasher.update(chunk)
            return hasher.hexdigest()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filename}")
        except IOError as e:
            raise IOError(f"Error reading file {filename}: {e}")

    def count_lines(self, filename: str) -> dict:
        """
        Counts total, non-empty, and empty lines in a text file.

        Args:
            filename (str): The path to the file.

        Returns:
            dict: A dictionary containing 'total_lines', 'non_empty_lines', 'empty_lines'.

        Raises:
            FileNotFoundError: If the file does not exist.
            IOError: If there's an issue reading the file.
        """
        total_lines = 0
        non_empty_lines = 0
        empty_lines = 0

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    total_lines += 1
                    if line.strip():  # Check if line is not just whitespace
                        non_empty_lines += 1
                    else:
                        empty_lines += 1
            return {
                'total_lines': total_lines,
                'non_empty_lines': non_empty_lines,
                'empty_lines': empty_lines
            }
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filename}")
        except IOError as e:
            raise IOError(f"Error reading file {filename}: {e}")
        except UnicodeDecodeError:
            raise IOError(f"Could not decode file {filename} with UTF-8. Consider specifying encoding.")

    def file_info(self, path_to_check: str) -> dict:
        """
        Retrieves basic information about a file or path.

        Args:
            path_to_check (str): The path to the file or directory.

        Returns:
            dict: A dictionary containing file information:
                  'path': The original path.
                  'exists': True if the path exists, False otherwise.
                  'is_file': True if the path is a file, False otherwise.
                  'is_dir': True if the path is a directory, False otherwise.
                  'size': Size in bytes if it's a file, None otherwise.
                  'last_modified_timestamp': Timestamp of last modification (seconds since epoch), None if path does not exist.
                  'last_modified_human': Human-readable last modification time, None if path does not exist.
                  'created_timestamp': Timestamp of creation (seconds since epoch), None if path does not exist.
                  'created_human': Human-readable creation time, None if path does not exist.
        """
        info = {
            'path': path_to_check,
            'exists': os.path.exists(path_to_check),
            'is_file': False,
            'is_dir': False,
            'size': None,
            'last_modified_timestamp': None,
            'last_modified_human': None,
            'created_timestamp': None,
            'created_human': None
        }

        if info['exists']:
            info['is_file'] = os.path.isfile(path_to_check)
            info['is_dir'] = os.path.isdir(path_to_check)

            try:
                stats = os.stat(path_to_check)
                if info['is_file']:
                    info['size'] = stats.st_size
                
                info['last_modified_timestamp'] = stats.st_mtime
                info['last_modified_human'] = time.ctime(stats.st_mtime)
                info['created_timestamp'] = stats.st_ctime
                info['created_human'] = time.ctime(stats.st_ctime)
            except OSError:
                # e.g., permission denied to get stats for some files/directories
                pass # Leave these fields as None or indicate an error if desired
        return info
