import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from decision_maker import BaseDecisionMaker, RuleBasedDecisionMaker

dm = RuleBasedDecisionMaker()

# 1. Assert interface contract
assert isinstance(dm, BaseDecisionMaker), "RuleBasedDecisionMaker must inherit from BaseDecisionMaker"

# 2. Test Cases across operations
test_cases = [
    # (input_prompt, expected_operation, expected_min_confidence)
    ("Hello there!", "DIRECT", 0.9),
    ("Remember that I dislike ketchup", "SAVE", 0.8),
    ("I prefer dark mode in all editors", "SAVE", 0.8),
    ("Actually, I now prefer light mode", "UPDATE", 0.8),
    ("Forget my dietary preferences", "DELETE", 0.8),
    ("Suggest a burger recipe", "RETRIEVE", 0.6),
    # Edge case: Conflicting intent (Save + Delete in same sentence)
    ("Remember to delete my old phone number", "UNCERTAIN", 0.0),
    # Edge case: Empty input
    ("", "DIRECT", 1.0)
]

for prompt, expected_op, min_conf in test_cases:
    decision = dm.decide(prompt)
    
    # Assert schema shape
    assert "operation" in decision
    assert "confidence" in decision
    assert "reason" in decision
    assert "extracted_data" in decision
    assert "raw_prompt" in decision
    
    # Assert routing behavior
    assert decision["operation"] == expected_op, (
        f"Failed for '{prompt}': Expected {expected_op}, got {decision['operation']}"
    )
    assert decision["confidence"] >= min_conf, (
        f"Confidence too low for '{prompt}': Expected >= {min_conf}, got {decision['confidence']}"
    )
    print(f"Passed: '{prompt}' -> {decision['operation']} (conf: {decision['confidence']:.2f})")

print("\nAll Decision Maker baseline assertions passed successfully!")