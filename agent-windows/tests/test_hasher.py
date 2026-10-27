import hashlib
import tempfile
from pathlib import Path
from hashing.hasher import FileHasher


def test_hasher_sha256_computation():
    hasher = FileHasher(max_size_mb=10)
    with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as f:
        content = "FIM Enterprise Security Baseline 2026 Test Content"
        f.write(content)
        f.flush()
        file_path = f.name

    try:
        expected_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        sha, size, mtime, status = hasher.compute_sha256(file_path)

        assert status == "success"
        assert sha == expected_hash
        assert size == len(content.encode("utf-8"))
        assert mtime is not None
    finally:
        Path(file_path).unlink(missing_ok=True)


def test_hasher_file_not_found():
    hasher = FileHasher()
    sha, size, mtime, status = hasher.compute_sha256("C:\\non_existent_file_path.xyz")
    assert status == "file_not_found"
    assert sha is None
