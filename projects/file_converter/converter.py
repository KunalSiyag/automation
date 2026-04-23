import json
import csv
from pathlib import Path
import os
import logging

# Configure logging for the converter module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Set to INFO for general operation, DEBUG for detailed troubleshooting

class FileConverter:
    """
    A utility class for converting between different file formats.
    Currently supports JSON and CSV.
    """
    def __init__(self):
        self.supported_formats = {"json", "csv"}

    def detect_format(self, filepath: str) -> str:
        """
        Detects the file format based on its extension.

        Args:
            filepath: The path to the file.

        Returns:
            The detected format as a string (e.g., "json", "csv").

        Raises:
            ValueError: If the file has no extension or an unsupported extension.
        """
        suffix = Path(filepath).suffix.lower()
        if not suffix:
            logger.error(f"File '{filepath}' has no extension. Cannot detect format.")
            raise ValueError(f"File '{filepath}' has no extension. Cannot detect format.")
        
        format_str = suffix[1:] # Remove the leading dot
        if format_str not in self.supported_formats:
            logger.error(f"Unsupported file format '{format_str}' for file '{filepath}'.")
            raise ValueError(f"Unsupported file format: {format_str}")
        
        return format_str

    def read_json(self, filepath: str) -> list[dict]:
        """
        Reads data from a JSON file.

        Args:
            filepath: The path to the JSON file.

        Returns:
            A list of dictionaries representing the JSON data.

        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If there are issues reading the file due to permissions.
            ValueError: If the file content is not valid JSON or has an unexpected structure.
            IOError: For other unexpected I/O errors.
        """
        if not os.path.exists(filepath):
            logger.error(f"JSON file not found: {filepath}")
            raise FileNotFoundError(f"JSON file not found: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                data = [data] # Wrap single JSON object in a list for consistent processing
            elif not isinstance(data, list):
                logger.error(f"Invalid JSON structure in '{filepath}'. Expected a list or object at root.")
                raise ValueError(f"Invalid JSON structure in '{filepath}'. Expected a list of objects or a single object.")
            
            logger.info(f"Successfully read JSON from {filepath}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in '{filepath}': {e}")
            raise ValueError(f"Invalid JSON format in '{filepath}': {e}") from e
        except PermissionError as e:
            logger.error(f"Permission denied to read JSON file: {filepath}. Error: {e}")
            raise PermissionError(f"Permission denied to read JSON file: {filepath}") from e
        except IOError as e:
            logger.error(f"Error reading JSON file '{filepath}': {e}")
            raise IOError(f"Error reading JSON file '{filepath}': {e}") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred while reading JSON file '{filepath}': {e}", exc_info=True)
            raise

    def write_json(self, data: list[dict], filepath: str):
        """
        Writes data to a JSON file.

        Args:
            data: A list of dictionaries to write.
            filepath: The path to the output JSON file.

        Raises:
            ValueError: If data cannot be serialized to JSON.
            PermissionError: If there are issues writing to the file due to permissions.
            IOError: For other unexpected I/O errors during writing.
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Successfully wrote JSON to {filepath}")
        except TypeError as e:
            logger.error(f"Data serialization error when writing JSON to '{filepath}': {e}")
            raise ValueError(f"Data cannot be serialized to JSON: {e}") from e
        except PermissionError as e:
            logger.error(f"Permission denied to write JSON file: {filepath}. Error: {e}")
            raise PermissionError(f"Permission denied to write JSON file: {filepath}") from e
        except IOError as e:
            logger.error(f"Error writing JSON file '{filepath}': {e}")
            raise IOError(f"Error writing JSON file '{filepath}': {e}") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred while writing JSON file '{filepath}': {e}", exc_info=True)
            raise

    def read_csv(self, filepath: str) -> list[dict]:
        """
        Reads data from a CSV file.

        Args:
            filepath: The path to the CSV file.

        Returns:
            A list of dictionaries, where each dictionary represents a row.

        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If there are issues reading the file due to permissions.
            ValueError: If the CSV file is malformed.
            IOError: For other unexpected I/O errors.
        """
        if not os.path.exists(filepath):
            logger.error(f"CSV file not found: {filepath}")
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            if not data and reader.fieldnames is None:
                logger.warning(f"CSV file '{filepath}' appears to be empty or contains only headers.")
            logger.info(f"Successfully read CSV from {filepath}")
            return data
        except csv.Error as e:
            logger.error(f"Malformed CSV format in '{filepath}': {e}")
            raise ValueError(f"Malformed CSV format in '{filepath}': {e}") from e
        except PermissionError as e:
            logger.error(f"Permission denied to read CSV file: {filepath}. Error: {e}")
            raise PermissionError(f"Permission denied to read CSV file: {filepath}") from e
        except IOError as e:
            logger.error(f"Error reading CSV file '{filepath}': {e}")
            raise IOError(f"Error reading CSV file '{filepath}': {e}") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred while reading CSV file '{filepath}': {e}", exc_info=True)
            raise

    def write_csv(self, data: list[dict], filepath: str):
        """
        Writes data (list of dictionaries) to a CSV file.

        Args:
            data: A list of dictionaries to write.
            filepath: The path to the output CSV file.

        Raises:
            ValueError: If the data is inconsistent for CSV writing or other CSV-related errors.
            PermissionError: If there are issues writing to the file due to permissions.
            IOError: For other unexpected I/O errors during writing.
        """
        try:
            fieldnames = []
            if data:
                # Collect all unique keys from all dictionaries to form the union of fieldnames
                all_keys = set()
                for row in data:
                    all_keys.update(row.keys())
                fieldnames = sorted(list(all_keys))
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if fieldnames: # Only write header if there are fieldnames
                    writer.writeheader()
                writer.writerows(data)
            logger.info(f"Successfully wrote CSV to {filepath}")
        except csv.Error as e:
            logger.error(f"Error writing CSV data to '{filepath}': {e}")
            raise ValueError(f"Error writing CSV data to '{filepath}': {e}") from e
        except PermissionError as e:
            logger.error(f"Permission denied to write CSV file: {filepath}. Error: {e}")
            raise PermissionError(f"Permission denied to write CSV file: {filepath}") from e
        except IOError as e:
            logger.error(f"Error writing CSV file '{filepath}': {e}")
            raise IOError(f"Error writing CSV file '{filepath}': {e}") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred while writing CSV file '{filepath}': {e}", exc_info=True)
            raise

    def convert(self, input_filepath: str, output_filepath: str):
        """
        Converts a file from one format to another.

        Args:
            input_filepath: The path to the input file.
            output_filepath: The path for the output file.

        Raises:
            ValueError: If input/output format is unsupported or file operations fail due to invalid data.
            NotImplementedError: If the specific conversion (input_format to output_format) is not implemented.
            FileNotFoundError: If the input file does not exist.
            PermissionError: If there are issues with file permissions.
            IOError: For other unexpected I/O errors during conversion.
        """
        input_format = self.detect_format(input_filepath)
        output_format = self.detect_format(output_filepath)

        if input_format == "json" and output_format == "csv":
            data = self.read_json(input_filepath)
            self.write_csv(data, output_filepath)
        elif input_format == "csv" and output_format == "json":
            data = self.read_csv(input_filepath)
            self.write_json(data, output_filepath)
        else:
            logger.error(f"Conversion from {input_format} to {output_format} is not implemented.")
            raise NotImplementedError(
                f"Conversion from {input_format} to {output_format} is not implemented or supported."
            )
