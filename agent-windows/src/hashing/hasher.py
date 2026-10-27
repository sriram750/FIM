import hashlib
import os
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Tuple, Optional


class FileHasher:
    def __init__(self, max_size_mb: int = 100, max_retries: int = 3, chunk_size: int = 65536):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_retries = max_retries
        self.chunk_size = chunk_size

    def compute_sha256(self, file_path: str) -> Tuple[Optional[str], int, Optional[str], str]:
        """
        Calculates SHA-256 hash, size, and modified timestamp of a file.
        Returns:
            Tuple[sha256_hash, file_size_bytes, modified_timestamp_iso, status]
            Status can be: "success", "file_not_found", "locked", "size_limit_exceeded", "permission_denied"
        """
        path = Path(file_path)
        if not path.is_file():
            return None, 0, None, "file_not_found"

        for attempt in range(self.max_retries):
            try:
                stat_result = path.stat()
                file_size = stat_result.st_size
                mtime = datetime.fromtimestamp(stat_result.st_mtime, tz=timezone.utc).isoformat()

                if file_size > self.max_size_bytes:
                    return None, file_size, mtime, "size_limit_exceeded"

                sha256 = hashlib.sha256()
                with open(file_path, "rb") as f:
                    while chunk := f.read(self.chunk_size):
                        sha256.update(chunk)

                return sha256.hexdigest(), file_size, mtime, "success"

            except (PermissionError, IOError) as e:
                # File is locked or being written to
                if attempt < self.max_retries - 1:
                    time.sleep(0.1 * (2 ** attempt))
                    continue
                else:
                    return None, 0, None, f"locked_or_permission_denied: {str(e)}"
            except Exception as e:
                return None, 0, None, f"error: {str(e)}"

        return None, 0, None, "failed_after_retries"
