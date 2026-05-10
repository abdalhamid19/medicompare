Verify this drug match:

DRUG A (from inventory): $drug_a
DRUG A parsed context: $drug_a_context

DRUG B (from tawreed): $drug_b$drug_b_ar_line
DRUG B parsed context: $drug_b_context

Algorithm context: $algorithm_context

Is this the SAME product? The Arabic name can help confirm the match if the
English name is ambiguous, but it cannot override a hard rejection conflict.

Return JSON only:
{"is_correct": true/false, "reason": "brief reason", "confidence": 0.0-1.0}
