import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from memory_service import create_source,attach_source_to_memory,get_memory_source

src = create_source(
    source_type="user_input",
    identifier="session_abc",
    metadata={"platform":"web_ui"}
)
print("source record id:",src["source_id"])

# linking with memory
linked = attach_source_to_memory(context_id=2,source_id=src["source_id"])
print("source attached suuccesfuly: ",linked)


sources=get_memory_source(2)
print("attached sources for memory 2")

for s in sources:
    print(f" source id : {s['source_id']} , type: {s['source_type']} , identifier: {s["identifier"]} , attached at : {s['attached_at']}")