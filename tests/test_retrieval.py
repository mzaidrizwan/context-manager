import sys
from pathlib import Path

# Add project root directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from memory_service import retrieve_memories

# Test 1: Relevant query must return matching memories
results_ketchup = retrieve_memories("ketchup", limit=5)
assert len(results_ketchup) > 0, "Retrieval failed: Expected at least 1 result for 'ketchup'."
assert results_ketchup[0]["score"] > 0, "Retrieval failed: Score must be greater than 0."
assert "ketchup" in results_ketchup[0]["content"].lower(), "Retrieval failed: Matched memory must contain query keyword."
print(f"Test 1 Passed: Retrieved {len(results_ketchup)} memories matching 'ketchup'.")

# Test 2: Unrelated query must return exactly 0 results
results_unrelated = retrieve_memories("telescope optics orbit mechanics")
assert len(results_unrelated) == 0, f"Retrieval failed: Expected 0 results for unrelated query, got {len(results_unrelated)}."
print("Test 2 Passed: Unrelated query returned 0 results.")

# Test 3: Respecting the limit parameter
results_limited = retrieve_memories("ketchup", limit=2)
assert len(results_limited) <= 2, f"Retrieval failed: Expected at most 2 results, got {len(results_limited)}."
print(f"Test 3 Passed: Limit parameter respected (returned {len(results_limited)} records).")

print("\nAll retrieval assertion tests passed successfully!")