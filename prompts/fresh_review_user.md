The first AI model was UNAVAILABLE and could NOT verify this drug match.
No first-AI decision was made; the algorithmic match was kept by default.

Please verify this match from scratch as the first available AI reviewer:

DRUG A (from inventory): $drug_a
DRUG A parsed context: $drug_a_context

DRUG B (from tawreed): $drug_b$drug_b_ar_line
DRUG B parsed context: $drug_b_context
Price context: $price_context

Is this the SAME product? Apply the strict pharmaceutical matching rules.

Return JSON only:
{"decision": "accept|reject", "is_correct": true/false, "reason": "brief reason", "confidence": 0.0-1.0, "hard_conflicts": [], "matched_fields": [], "mismatched_fields": []}
