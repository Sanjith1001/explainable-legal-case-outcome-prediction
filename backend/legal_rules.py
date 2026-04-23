"""
Legal Rule Engine — Layer 4
Domain rules that adjust prediction based on legal principles.
"""

import re

# ── Legal rules ────────────────────────────────────────────────
LEGAL_RULES = [
    {
        "name"      : "Benefit of doubt",
        "keywords"  : ["benefit of doubt","reasonable doubt","two views possible",
                       "not proven beyond","doubt","acquittal"],
        "direction" : "accepted",
        "weight"    : 0.06,
        "note"      : "Benefit of doubt principle detected",
    },
    {
        "name"      : "Constitutional rights",
        "keywords"  : ["article 21","article 14","article 19","fundamental right",
                       "right to life","right to equality","constitutional"],
        "direction" : "accepted",
        "weight"    : 0.08,
        "note"      : "Constitutional rights violation detected",
    },
    {
        "name"      : "Procedural violation",
        "keywords"  : ["section 50 crpc","illegal arrest","no warrant","rights not informed",
                       "custody violation","procedure not followed","illegal search"],
        "direction" : "accepted",
        "weight"    : 0.07,
        "note"      : "Procedural violation detected",
    },
    {
        "name"      : "Strong forensic evidence",
        "keywords"  : ["dna","forensic","fingerprint","ballistic","post mortem",
                       "medical evidence","scientific evidence","expert witness"],
        "direction" : "rejected",
        "weight"    : 0.05,
        "note"      : "Strong forensic evidence detected",
    },
    {
        "name"      : "Confession",
        "keywords"  : ["confession","confessed","admitted guilt","pleaded guilty",
                       "voluntary confession"],
        "direction" : "rejected",
        "weight"    : 0.07,
        "note"      : "Confession detected — weakens appeal",
    },
    {
        "name"      : "Acquittal appeal",
        "keywords"  : ["appeal against acquittal","state appeal","acquitted by",
                       "challenging acquittal"],
        "direction" : "rejected",
        "weight"    : 0.05,
        "note"      : "State appeal against acquittal — typically harder to succeed",
    },
    {
        "name"      : "High court dismissed",
        "keywords"  : ["high court dismissed","dismissed by high court",
                       "high court upheld conviction","affirmed by high court"],
        "direction" : "rejected",
        "weight"    : 0.04,
        "note"      : "Two courts have already rejected — harder to succeed",
    },
    {
        "name"      : "Delay / limitation",
        "keywords"  : ["barred by limitation","time barred","inordinate delay",
                       "unexplained delay","filed after"],
        "direction" : "rejected",
        "weight"    : 0.06,
        "note"      : "Delay / limitation issue detected",
    },
]


class LegalRuleEngine:

    def apply_rules(self, text: str, current_prob_accepted: float) -> dict:
        """
        Applies legal domain rules to adjust prediction probability.
        Returns adjusted probability + list of triggered rules.
        """
        text_lower     = text.lower()
        triggered      = []
        prob_adjustment = 0.0

        for rule in LEGAL_RULES:
            hits = sum(1 for kw in rule["keywords"] if kw in text_lower)
            if hits > 0:
                direction  = rule["direction"]
                weight     = rule["weight"] * min(hits, 2)  # cap at 2x
                triggered.append({
                    "rule"      : rule["name"],
                    "note"      : rule["note"],
                    "direction" : direction,
                    "weight"    : round(weight, 3),
                })
                if direction == "accepted":
                    prob_adjustment += weight
                else:
                    prob_adjustment -= weight

        # Apply adjustment (cap between 0.15 and 0.92)
        adjusted_prob = current_prob_accepted + prob_adjustment
        adjusted_prob = max(0.15, min(adjusted_prob, 0.92))

        return {
            "adjusted_prob_accepted": round(adjusted_prob, 4),
            "triggered_rules"       : triggered,
            "total_adjustment"      : round(prob_adjustment, 4),
        }
