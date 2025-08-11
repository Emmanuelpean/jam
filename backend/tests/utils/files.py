"""
File loading utilities for test data
"""

import base64
import mimetypes
from pathlib import Path


def get_resources_path() -> Path:
    """Get the path to the resources folder"""

    current_dir = Path(__file__).parent
    return current_dir / "../resources"


def load_file_as_base64(filename: str) -> str | None:
    """Load a file from the resources folder and return as base64 string"""
    resources_path = get_resources_path()
    file_path = resources_path / filename

    try:
        with open(file_path, "rb") as file:
            file_content = file.read()
            return base64.b64encode(file_content).decode("utf-8")
    except Exception as e:
        print(f"❌ Error reading file {filename}: {e}")
        return None


def get_file_info(filename) -> tuple[int | None, str | None]:
    """Get file size and MIME type"""

    resources_path = get_resources_path()
    file_path = resources_path / filename

    if not file_path.exists():
        return None, None

    try:
        # Get file size
        file_size = file_path.stat().st_size

        # Get MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type is None:
            # Default MIME types for common file extensions
            ext = file_path.suffix.lower()
            mime_defaults = {
                ".pdf": "application/pdf",
                ".doc": "application/msword",
                ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ".txt": "text/plain",
            }
            mime_type = mime_defaults.get(ext, "application/octet-stream")

        return file_size, mime_type
    except Exception as e:
        print(f"❌ Error getting file info for {filename}: {e}")
        return None, None


def load_all_resource_files() -> dict[str, dict[str, str | int]]:
    """Load all files from the resources folder"""

    resources_path = get_resources_path()
    loaded_files = {}

    print(f"📁 Loading files from: {resources_path}")

    for file_path in resources_path.iterdir():
        if file_path.is_file():
            file_content = load_file_as_base64(file_path.name)
            file_size, mime_type = get_file_info(file_path.name)

            if file_content:
                loaded_files[file_path.name] = {"content": file_content, "size": file_size, "type": mime_type}
                print(f"✅ Loaded: {file_path.name} ({file_size} bytes, {mime_type})")
            else:
                print(f"❌ Failed to load: {file_path.name}")

    if not loaded_files:
        print("📂 No files found in resources folder")
    else:
        print(f"📊 Total files loaded: {len(loaded_files)}")

    return loaded_files
