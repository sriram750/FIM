import tempfile
from pathlib import Path
from spool.db import LocalSpool
from hashing.hasher import FileHasher
from baseline.scanner import BaselineScanner




def test_baseline_creation_and_mismatch_detection():
    with tempfile.TemporaryDirectory() as tmp_dir:
        spool_path = Path(tmp_dir) / "spool.db"
        baseline_path = Path(tmp_dir) / "baseline.db"
        watched_dir = Path(tmp_dir) / "watched"
        watched_dir.mkdir()

        test_file = watched_dir / "protected_driver.sys"
        test_file.write_text("v1.0.0 Original Secure Content")

        spool = LocalSpool(db_path=spool_path)
        hasher = FileHasher()
        scanner = BaselineScanner(spool, hasher, db_path=baseline_path)

        # 1. Initial scan
        stats1 = scanner.run_full_scan([str(watched_dir)])
        assert stats1["files_scanned"] == 1
        assert stats1["new_baselines"] == 1
        assert stats1["mismatches"] == 0

        # Check that baseline_created event was enqueued
        events = spool.peek_batch(10)
        assert len(events) == 1
        assert events[0]["event_type"] == "baseline_created"

        # 2. Tamper with file
        test_file.write_text("v1.0.0 MALICIOUSLY ALTERED CONTENT")

        # 3. Rescan to detect drift
        stats2 = scanner.run_full_scan([str(watched_dir)])
        assert stats2["mismatches"] == 1

        # Check that integrity_mismatch event was enqueued
        events_after = spool.peek_batch(10)
        assert len(events_after) == 2
        assert events_after[1]["event_type"] == "integrity_mismatch"
        assert events_after[1]["old_sha256_hash"] is not None
