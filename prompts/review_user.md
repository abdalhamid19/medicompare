Review this AI decision about a drug match:

DRUG A (from inventory): $drug_a
DRUG A parsed context: $drug_a_context

DRUG B (from tawreed): $drug_b$drug_b_ar_line
DRUG B parsed context: $drug_b_context
Price context: $price_context

First AI decided: $first_decision_text
First AI confidence: $first_confidence
First AI reason: $first_reason

Do you AGREE with the first AI? Apply the same strict pharmaceutical matching
rules.

Return JSON only:
{"decision": "agree|disagree", "agree": true/false, "reason": "brief reason", "confidence": 0.0-1.0, "hard_conflicts": [], "matched_fields": [], "mismatched_fields": []}
