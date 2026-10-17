import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from memory_service import create_category, assign_category_to_memory, retrieve_memories

# create burger named category
cat = create_category("burger", description="burger and fast food preferences")
print(f"category created/retrieved: id={cat['category_id']}-{cat['name']}")

#assign category to memory id # 2
assigned = assign_category_to_memory(context_id=2,category_id=cat["category_id"])
print(f"category assigned to memory 2: {assigned}")

#search for 'suggest a burger recipe'
results = retrieve_memories("Suggest a burger recipe",limit=5)
print(f"\n retrieved {len(results)} memories for prompt 'Suggest a burger recipe':")
for r in results:
    print(f" [id {r['context_id']}] {r['subject']} : {r['content']} | categories: '{r['categories']}' (Score: {r['score']})")

assert len(results)>0, "Failed: Expected Memory 2 to be retrieved via 'burger' category match."
assert results[0]["context_id"]==2,"Failed: Top result must be Memory ID 2."
print("\nAssertion passed: 'burger recipe' successfully retrieved dietary preference via category taxonomy!")