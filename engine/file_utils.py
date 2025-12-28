import json
import os
import tempfile
from typing import Any, Dict


def safe_write_json(filepath: str, data: Dict[str, Any]) -> None:
    """
    Write JSON data to a temporary file and atomically replace the destination.

    This mirrors the durability approach used in Match._safe_write_json, ensuring
    that partially written files are not persisted.
    """
    directory = os.path.dirname(filepath) or "."
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix="uqw_", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w") as tmp_file:
            json.dump(data, tmp_file, indent=2)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
        os.replace(tmp_path, filepath)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
