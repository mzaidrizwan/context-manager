import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from context_manager import ContextManager

cm = ContextManager()

# 1. direct pass-through
res1 = cm.process_prompt("hello assistant")
assert res1["operation"] =="DIRECT"
assert res1["status"] == "success"
assert len(res1["retrieved_context"])==0
print("test#1 passed: direct path work")

# 2 retrieve dietry context for recipe
res2=cm.process_prompt("sugggest a burger recipe")
assert res2["operation"] == "RETRIEVE"
assert res2["status"]=="success"
assert len(res2["retrieved_context"])>0
print(f"test#2 passed: retrieved path works (found {len(res2['retrieved_context'])} memories)")

#3 save new preference
res3=cm.process_prompt("remember that i prefer morning meetings")
assert res3["operation"]=="SAVE"
assert res3["status"]=="success"
assert "context_id" in res3["execution_result"]
print(f"test#3 passed: SAVE path works (created context_id {res3['execution_result']['context_id']})")

#4 UNCERTAIN fallback handling
res4 = cm.process_prompt("remember to delete my old phone number")
assert res4["operation"]=="UNCERTAIN"
assert res4["status"] =="fallback"
print("test#4 passed: UNCERTAIN fallback handled safely")


print("\n all context manager orchestration assertions passed successfully")