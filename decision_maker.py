from abc import ABC, abstractmethod
import re

class BaseDecisionMaker(ABC):
    @abstractmethod
    def decide(self,prompt:str)->dict:
        pass

class RuleBasedDecisionMaker(BaseDecisionMaker):
    VALID_OPERATIONS =  {"DIRECT", "RETRIEVE", "SAVE", "UPDATE", "DELETE", "UNCERTAIN"}

    def decide(self,prompt:str)->dict:
        if not prompt or not prompt.strip():
            return {
                "operation":"DIRECT",
                "confidence":1.0,
                "reason":"Empty prompt passed; no context operation required",
                "extracted_data":{},
                "raw_prompt":prompt or ""
            }

        raw_prompt = prompt.strip()
        lower = raw_prompt.lower()

        # if user gives conflicting instruction in a single prompt
        has_save = bool(re.search(r"\b(remember|save|keep in mind)\b",lower))
        has_delete = bool(re.search(r"\b(forget|delete|remove|erase)",lower))
        
        if has_delete and has_save:
            return{
                "operation": "UNCERTAIN",
                "confidence": 0.3,
                "reason": "Conflicting intent detected (both save and delete signals found).",
                "extracted_data": {},
                "raw_prompt": raw_prompt
            }
        
        # delete/forget intent
        delete_patterns = [
            r"\b(forget|delete|remove|erase)\b.*\b(memory|preference|fact|that)\b",
            r"^forget\s+(about\s+)?(?P<target>.+)",
            r"^delete\s+(my\s+)?(?P<target>.+)"
        ]
        for pat in delete_patterns:
            m = re.search(pat,lower)
            if m:
                target = m.groupdict().get("target","").strip() or raw_prompt
                return{
                    "operation": "DELETE",
                    "confidence": 0.9,
                    "reason": "Explicit memory removal intent detected.",
                    "extracted_data": {"target": target},
                    "raw_prompt": raw_prompt
                }

        # update intent
        update_patterns = [
            r"^actually,?\s+(?P<content>.+)",
            r"\b(change|update|switch|modify)\s+(my\s+)?(?P<content>.+)",
            r"^i\s+now\s+(prefer|like|use)\s+(?P<content>.+)",
            r"\b(prefer|want)\s+(?P<content>.+)\s+instead\b",
            r"\b(actually|instead)\b.*\b(prefer|like|want)\b"
        ]
        for pat in update_patterns:
            m= re.search(pat,lower)
            if m:
                content = m.groupdict().get("content","").strip() or raw_prompt
                return {
                    "operation": "UPDATE",
                    "confidence": 0.85,
                    "reason": "Explicit preference modification intent detected.",
                    "extracted_data": {"content": content},
                    "raw_prompt": raw_prompt
                }
        
        # save intent
        save_patterns=[
            r"\bremember\s+(that\s+)?(?P<content>.+)",
            r"\bkeep\s+in\s+mind\s+(that\s+)?(?P<content>.+)",
            r"\bnote\s+that\s+(?P<content>.+)",
            r"^i\s+(prefer|dislike|hate|love|am allergic to)\s+(?P<content>.+)",
            r"^my\s+(favorite|preferred|email|name|phone)\s+(?P<content>.+)"
        ]
        for pat in save_patterns:
            m=re.search(pat,lower)
            if m:
                extracted_content= m.groupdict().get("content","")
                return{
                    "operation":"SAVE",
                    "confidence":0.9,
                    "reason":"Explicit storage intent detected",
                    "extracted_data":{
                        "subject":"user_preference"
                        ,"content":extracted_content
                    },
                    "raw_prompt":raw_prompt
                }

        
        # direct intent (greeting, casual small talks)
        direct_patterns = [
            r"^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening)|howdy)(\s+(there|everyone|all|assistant|bot|ai|friend))?[\s!.,?]*$",
            r"^how\s+are\s+you(\s+doing)?\??$",
            r"^what\s+can\s+you\s+do\??$",
            r"^(thanks|thank you|ok|okay)[\s!.]*$"
        ]
        for pat in direct_patterns:
            if re.match(pat,lower):
                return{
                    "operation":"DIRECT",
                    "confidence":0.95,
                    "reason":"Generic greeting or conversational filter",
                    "extracted_data":{},
                    "raw_prompt":raw_prompt
                }

        # any query asking a domain question or seeking an answer
        return{
            "operation":"RETRIEVE",
            "confidence":0.7,
            "reason":"informational or task-orented quesry that may benifit from prior context",
            "extracted_data":{"query":raw_prompt},
            "raw_prompt":raw_prompt
        }