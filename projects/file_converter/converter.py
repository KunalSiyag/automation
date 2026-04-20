import json
import csv
from pathlib import Path

class FileConverter:
    """
    A utility class for converting between different file formats.
    Currently supports JSON to CSV conversion.
    """
    def __init__(self):
        self.supported_formats = {"json", "csv"}
        # In a real application, you might load conversion strategies dynamically

    def detect_format(self, file_path: str) -> str:
        """
        Detects the file format based on its extension.

        Args:
            file_path: The path to the file.

        Returns:
            The detected format as a lowercase string (e.g., 'json', 'csv').

        Raises:
            ValueError: If the file has no extension or an unsupported extension.
        """
        suffix = Path(file_path).suffix
        if not suffix:
            raise ValueError(f"File '{file_path}' has no extension. Cannot detect format.")
        
        file_format = suffix[1:].lower()
        if file_format not in self.supported_formats:
            raise ValueError(f"Unsupported file format: .{file_format}. Supported formats are {', '.join(sorted(self.supported_formats))}")
        return file_format

    def read_json(self, file_path: str):
        """
        Reads data from a JSON file.

        Args:
            file_path: The path to the JSON file.

        Returns:
            The data loaded from the JSON file.

        Raises:
            IOError: If the file cannot be read.
            json.JSONDecodeError: If the file content is not valid JSON.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise IOError(f"JSON file not found: {file_path}")
        except json.JSONDecodeError as e:
            # Re-raise with more context
            raise json.JSONDecodeError(f"Invalid JSON format in '{file_path}': {e}", e.doc, e.pos)
        except Exception as e:
            raise IOError(f"Error reading JSON file '{file_path}': {e}")

    def write_csv(self, data: list[dict], file_path: str):
        """
        Writes a list of dictionaries to a CSV file.

        Args:
            data: A list of dictionaries, where each dictionary represents a row.
            file_path: The path to the output CSV file.

        Raises:
            ValueError: If the data is empty or not in the expected format.
            IOError: If the file cannot be written.
        """
        if not data:
            # It's generally fine to write an empty CSV with just headers if data is empty.
            # But for conversion, empty input might mean empty output or an error.
            # For now, let's allow it to create an empty CSV with headers.
            fieldnames = [] # No data means no inferred fieldnames
        elif not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
            raise ValueError("CSV data must be a list of dictionaries.")
        else:
            # Assume all dictionaries have the same keys for headers
            # Or, collect all unique keys from all dictionaries
            fieldnames = list(data[0].keys() if data else [])
            # A more robust approach would collect all keys from all dicts to ensure all columns are present
            # all_keys = set()
            # for row in data:
            #     all_keys.update(row.keys())
            # fieldnames = sorted(list(all_keys))

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                if data:
                    writer.writerows(data)
        except Exception as e:
            raise IOError(f"Error writing CSV file '{file_path}': {e}")

    def convert(self, input_file_path: str, output_file_path: str):
        """
        Converts a file from one format to another.

        Args:
            input_file_path: The path to the input file.
            output_file_path: The path where the converted file will be saved.

        Raises:
            ValueError: If input/output formats are invalid or unsupported by detection.
            NotImplementedError: If the specific conversion is not yet implemented.
            IOError: If file reading/writing fails.
        """
        input_format = self.detect_format(input_file_path)
        output_format = self.detect_format(output_file_path)

        if input_format == "json" and output_format == "csv":
            data = self.read_json(input_file_path)
            self.write_csv(data, output_file_path)
        # Add more conversion logic here as needed
        # elif input_format == "csv" and output_format == "json":
        #     data = self.read_csv(input_file_path) # Need to implement read_csv
        #     self.write_json(data, output_file_path) # Need to implement write_json
        else:
            raise NotImplementedError(
                f"Conversion from {input_format.upper()} to {output_format.upper()} is not yet supported. "
                f"Currently, only JSON to CSV is implemented." # Updated message for clarity
            )
