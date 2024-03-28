"""pytest configuration for code_explainer project."""
import sys
from pathlib import Path

# Add project root to Python path so local imports work
sys.path.insert(0, str(Path(__file__).parent))
