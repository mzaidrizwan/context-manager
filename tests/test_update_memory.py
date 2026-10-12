import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from memory_service import update_memory

updated= update_memory(
    context_id=2,
    content="I dislike ketchup and mayonnaise",
    confidence=0.99
)

print("updated memory successfully:")
print(f"ID: {updated['context_id']}")
print(f"Content: {updated['content']}")
print(f"Confidence: {updated['confidence']}")
print(f"Updated at: {updated['updated_at']}")
