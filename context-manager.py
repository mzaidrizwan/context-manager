from decision_maker import BaseDecisionMaker, RuleBasedDecisionMaker
from memory_service import (
    create_memory,
    retrieve_memories,
    soft_delete_memory,
    list_memories
)

class ContextManager:
    """
    Coordinates context lifecycle:
    Evaluates prompts using a Decision Maker and executes safe database operations.
    """
    def __init__(self, decision_maker: BaseDecisionMaker = None):
        self.decision_maker = decision_maker or RuleBasedDecisionMaker()

    def process_prompt(self, prompt: str) -> dict:
        """
        Main orchestration pipeline.
        1. Classifies intent via Decision Maker.
        2. Validates decision schema.
        3. Executes corresponding database or retrieval action.
        4. Returns unified execution envelope.
        """
        # Step 1: Pure classification
        decision = self.decision_maker.decide(prompt)
        op = decision.get("operation")
        reason = decision.get("reason", "")
        extracted = decision.get("extracted_data", {})
        raw_prompt = decision.get("raw_prompt", prompt)

        envelope = {
            "prompt": raw_prompt,
            "operation": op,
            "decision_reason": reason,
            "retrieved_context": [],
            "execution_result": {},
            "status": "success"
        }

        # Step 2: Execution dispatch
        if op == "DIRECT":
            envelope["execution_result"] = {"message": "Direct pass-through; no context required."}
            return envelope

        elif op == "RETRIEVE":
            query = extracted.get("query", raw_prompt)
            memories = retrieve_memories(query=query, limit=5)
            envelope["retrieved_context"] = memories
            envelope["execution_result"] = {"count": len(memories)}
            return envelope

        elif op == "SAVE":
            subject = extracted.get("subject", "user_note")
            content = extracted.get("content", raw_prompt)
            # Store with standard initial confidence
            saved = create_memory(
                subject=subject,
                content=content,
                memory_type="preference",
                confidence=decision.get("confidence", 0.9)
            )
            envelope["execution_result"] = {
                "context_id": saved["context_id"],
                "subject": saved["subject"],
                "content": saved["content"]
            }
            return envelope

        elif op == "DELETE":
            target = extracted.get("target", "").strip()
            # Find candidate active memories to delete based on the target keyword
            candidates = retrieve_memories(query=target, limit=1) if target else []
            if candidates:
                target_id = candidates[0]["context_id"]
                deleted = soft_delete_memory(target_id)
                envelope["execution_result"] = {
                    "context_id": target_id,
                    "action": "soft_deleted",
                    "subject": deleted["subject"]
                }
            else:
                envelope["status"] = "fallback"
                envelope["execution_result"] = {
                    "action": "none",
                    "message": f"No active memory found matching '{target}' to delete."
                }
            return envelope

        elif op == "UPDATE":
            content = extracted.get("content", raw_prompt)
            # For baseline, retrieve candidate memory to update
            candidates = retrieve_memories(query=content, limit=1)
            envelope["execution_result"] = {
                "action": "update_flagged",
                "target_candidates": [c["context_id"] for c in candidates],
                "proposed_content": content
            }
            return envelope

        elif op == "UNCERTAIN":
            envelope["status"] = "fallback"
            envelope["execution_result"] = {
                "action": "none",
                "message": "Decision uncertain; routed as plain conversational query."
            }
            return envelope

        else:
            # Defensive branch for unexpected operations
            envelope["status"] = "error"
            envelope["execution_result"] = {"error": f"Unknown operation: {op}"}
            return envelope