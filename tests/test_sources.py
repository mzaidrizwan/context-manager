import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from memory_service import create_source,attach_source_to_memory

src = create_source(
    source_type="user_input",
    identifier="session_abc",
    metadata={"platform":"web_ui"}
)
print("source record id:",src["source_id"])

# linking with memory
linked = attach_source_to_memory(context_id=2,source_id=src["source_id"])
print("source attached suuccesfuly: ",linked)