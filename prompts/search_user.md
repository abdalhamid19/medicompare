Given this drug from inventory: "$drug_name"
Inventory parsed context: $inventory_context

Which of these candidates is the CORRECT match? Consider brand name, dosage,
quantity, volume, weight, form, route, variants, import status, and flavor.

Candidates:
$candidates_text

Return JSON only:
{"best_index": 1-$max_index, "reason": "brief reason", "confidence": 0.0-1.0}

If NONE are correct or the evidence is ambiguous, set best_index to 0.
