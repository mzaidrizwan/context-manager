import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from memory_service import soft_delete_memory, restore_memory,list_memories,get_memory_history

# soft delete memory
del_res = soft_delete_memory(2)
print("soft deleted status: ",del_res["status"])

# checking if list_memories() is not showing soft-deleted memory
active_list = list_memories()
print("active count after soft-delete ",len(active_list))

# restore memory
rest_res = restore_memory(2)
print("restored status: ",rest_res["status"])

# checking if list_memories() now again showing it
active_list_after = list_memories()
print("available active memories after restoration is ",len(active_list_after))

history = get_memory_history(2)
print(f"available memory_history is {len(history)}")