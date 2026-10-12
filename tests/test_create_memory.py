import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from memory_service import create_memory

memory= create_memory(
    subject="dietary_performance",
    content="I dislike ketchup",
    memory_type="preference",
    confidence=0.95,
    metadata={"source_channel":"chat"}
)

print("memory created")
print(f"ID: {memory['context_id']}")
print(f"subject: {memory['subject']}")
print(f"content : {memory['content']}")
print(f"status: {memory['status']}")