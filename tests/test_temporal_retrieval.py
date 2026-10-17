import sys
from datetime import datetime,timedelta,timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from memory_service import create_memory,retrieve_memories,soft_delete_memory

now = datetime.now(timezone.utc)

# create an already expired memory
expired_mem = create_memory(
    subject="temporary_diet",
    content="avoid sugar completely during fasting window",
    memory_type="preference",
    confidence=0.9,
    expires_at=now - timedelta(days=1)
)
print("expired memory created with id = ",expired_mem["context_id"])

#create a future valid memory
future_mem= create_memory(
    subject="upcoming_trip",
    content="staying in downtown chicago hotel",
    memory_type="fact"
    ,confidence=0.9,
    valid_after=now+timedelta(days=7) # valid next week
)
print("created future valid memory of id : ",future_mem["context_id"])

# fasting window should'nt retrieve expired memory
results_expired = retrieve_memories("fasting window")
expired_ids =[r["context_id"] for r in results_expired]
assert expired_mem["context_id"] not in expired_ids,"failed: expired memory was retrieved"
print("assertion passed, expired memory excluded")

# 'chicago hotel' should'nt retrieve future memory
results_future = retrieve_memories("chicago hotel")
future_ids = [r["context_id"] for r in results_future]
assert future_mem["context_id"] not in future_ids, "Failed: Future-valid memory was retrieved"
print("Assertion Passed: Future-valid memory was properly excluded.")

# Test Soft-Delete Exclusion
soft_delete_memory(2)
results_deleted = retrieve_memories("Suggest a burger recipe")
deleted_ids = [r["context_id"] for r in results_deleted]
assert 2 not in deleted_ids, "Failed: Soft-deleted memory was retrieved!"
print("Assertion Passed: Soft-deleted memory was properly excluded.")

# Restore memory 2 back to active
from memory_service import restore_memory
restore_memory(2)
results_restored = retrieve_memories("Suggest a burger recipe")
restored_ids = [r["context_id"] for r in results_restored]
assert 2 in restored_ids, "Failed: Restored memory should be retrievable!"
print("Assertion Passed: Restored memory is retrievable again.")

print("\nAll temporal and lifecycle retrieval tests passed successfully!")