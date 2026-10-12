import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from memory_service import get_memory,list_memories

# fetch memory by providing context_id as parameter
mem = get_memory(2)
print("fetched memory of asked context_id: ")
print(mem)

# list all active memories
all_active=list_memories()
print(f"\nTotal Active memories: {len(all_active)}")
for item in all_active:
    print(f" [{item['context_id']}  {item['subject']}: {item['content']} (Status: {item['status']})")
    