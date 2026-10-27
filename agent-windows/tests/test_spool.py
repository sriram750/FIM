import os
import tempfile
from pathlib import Path
from spool.db import LocalSpool


def test_spool_enqueue_and_acknowledge():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_spool.db"
        spool = LocalSpool(db_path=db_path)

        assert spool.get_queue_depth() == 0

        # Enqueue 2 events
        id1 = spool.enqueue_event("file_created", {"file_path": "C:\\test\\file1.txt", "file_name": "file1.txt"})
        id2 = spool.enqueue_event("file_modified", {"file_path": "C:\\test\\file2.txt", "file_name": "file2.txt"})

        assert spool.get_queue_depth() == 2

        # Peek batch
        batch = spool.peek_batch(limit=10)
        assert len(batch) == 2
        assert batch[0]["event_id"] == id1
        assert batch[0]["sequence_number"] == 1
        assert batch[1]["event_id"] == id2
        assert batch[1]["sequence_number"] == 2

        # Acknowledge first event
        deleted = spool.acknowledge_events([id1])
        assert deleted == 1
        assert spool.get_queue_depth() == 1

        # Peek remaining
        remaining = spool.peek_batch(limit=10)
        assert len(remaining) == 1
        assert remaining[0]["event_id"] == id2
