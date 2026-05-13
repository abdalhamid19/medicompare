Given this drug from inventory: "$drug_name"
Inventory parsed context: $inventory_context
Inventory price: $inventory_price

Which of these candidates is the CORRECT match? Consider brand name, dosage,
quantity, volume, weight, form, route, variants, import status, and flavor.
Use price only as a tie-breaker between otherwise compatible candidates.

Candidates:
$candidates_text

Return JSON only:
{"decision": "accept|reject", "best_index": 0, "reason": "brief reason", "confidence": 0.0-1.0, "hard_conflicts": [], "matched_fields": [], "mismatched_fields": []}

`best_index` must be a JSON number only, not a string and not a range.
Valid examples: 0, 1, 2. Invalid examples: "1", "1-$max_index", "1-1",
"candidate 1".

If NONE are correct or the evidence is ambiguous, set best_index to 0.
