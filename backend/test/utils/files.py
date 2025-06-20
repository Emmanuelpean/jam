"""
File loading utilities for test data
"""

import base64
import mimetypes
from pathlib import Path


def get_resources_path():
    """Get the path to the resources folder"""
    current_dir = Path(__file__).parent
    resources_dir = current_dir / "../resources"

    # Create resources directory if it doesn't exist
    resources_dir.mkdir(exist_ok=True)

    return resources_dir


def load_file_as_bytes(filename):
    """Load a file from resources folder and return as bytes"""
    resources_path = get_resources_path()
    file_path = resources_path / filename

    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return None

    try:
        with open(file_path, "rb") as file:
            file_content = file.read()
            return file_content  # Return raw bytes, not base64
    except Exception as e:
        print(f"❌ Error reading file {filename}: {e}")
        return None


def get_file_info(filename):
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


def load_all_resource_files():
    """Load all files from the resources folder"""
    resources_path = get_resources_path()
    loaded_files = {}

    print(f"📁 Loading files from: {resources_path}")

    if not resources_path.exists():
        print(f"📂 Resources folder created at: {resources_path}")
        return loaded_files

    for file_path in resources_path.iterdir():
        if file_path.is_file():
            filename = file_path.name
            file_content = load_file_as_bytes(filename)  # Get bytes, not base64
            file_size, mime_type = get_file_info(filename)

            if file_content:
                loaded_files[filename] = {"content": file_content, "size": file_size, "type": mime_type}
                print(f"✅ Loaded: {filename} ({file_size} bytes, {mime_type})")
            else:
                print(f"❌ Failed to load: {filename}")

    if not loaded_files:
        print("📂 No files found in resources folder")
    else:
        print(f"📊 Total files loaded: {len(loaded_files)}")

    return loaded_files


def create_placeholder_content(description):
    """Create placeholder base64 content for missing files"""
    placeholder_text = f"PLACEHOLDER FILE CONTENT\n\n{description}\n\nThis is a placeholder file created because the actual file was not found in the resources folder."
    return base64.b64encode(placeholder_text.encode("utf-8")).decode("utf-8")


if __name__ == "__main__":
    # Test the file loader
    files = load_all_resource_files()
    if files:
        print("\nLoaded files:")
        for filename, info in files.items():
            print(f"  {filename}: {len(info['content'])} chars base64, {info['size']} bytes, {info['type']}")
    else:
        print("\nNo files loaded. Check the resources folder.")
