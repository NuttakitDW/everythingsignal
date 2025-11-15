# api/walrus_client.py

import json
import uuid
from typing import Dict, Any


def upload_artifact(artifact: Dict[str, Any]) -> str:
    """
    Stub for Walrus upload.

    For now, just:
      - JSON-dump the artifact (to prove it serializes)
      - return a fake walrus:// ID

    Later: Replace with real Walrus SDK / HTTP call.
    """
    _ = json.dumps(artifact)  # ensure serializable
    fake_id = f"walrus://{uuid.uuid4()}"
    return fake_id
