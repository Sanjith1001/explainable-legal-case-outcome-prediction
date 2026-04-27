"""
Legal Argument Simulator

Grounded simulator that:
- categorizes the submitted argument
- checks retrieved cases for supporting patterns
- considers triggered legal rules from the current prediction
- explains confidence shifts in evidence-oriented language
"""

from __future__ import annotations

import re
from typing import Any

# Legal keywords -> argument categories
ARGUMENT_PATTERNS = {
    "alibi": {
        "keywords": ["alibi", "was not present", "not at scene", "witness confirms absence", "whereabouts"],
        "weight": 0.08,
        "direction": "accepted",
        "response": (
            "Alibi is legally significant, but it is persuasive only when independently corroborated. "
            "Courts usually expect more than a bare denial."
        ),
    },
    "procedural_violation": {
        "keywords": ["procedure not followed", "violated", "illegal arrest", "section 50 crpc",
                     "rights violated", "not informed", "no warrant", "illegal search"],
        "weight": 0.10,
        "direction": "accepted",
        "response": (
            "Procedural violations can materially weaken the prosecution or strengthen a challenge "
            "to the impugned order, especially when statutory safeguards were ignored."
        ),
    },
    "weak_evidence": {
        "keywords": ["weak evidence", "no direct evidence", "circumstantial only", "insufficient proof",
                     "no eyewitness", "unreliable witness", "contradictory testimony", "hearsay"],
        "weight": 0.09,
        "direction": "accepted",
        "response": (
            "Weak or incomplete evidence is a serious appellate issue, particularly where the chain "
            "of circumstances is incomplete or witness credibility is unstable."
        ),
    },
    "benefit_of_doubt": {
        "keywords": ["benefit of doubt", "reasonable doubt", "not proven beyond", "doubt exists",
                     "probability of innocence", "cannot be certain"],
        "weight": 0.12,
        "direction": "accepted",
        "response": (
            "Benefit of doubt is one of the strongest defense-oriented principles in Indian criminal law. "
            "If two plausible views exist, the one favouring the accused carries real force."
        ),
    },
    "strong_evidence": {
        "keywords": ["strong evidence", "direct evidence", "eyewitness", "forensic proof",
                     "dna match", "fingerprint", "cctv", "caught red handed", "confession"],
        "weight": 0.10,
        "direction": "rejected",
        "response": (
            "Strong direct or forensic evidence usually stabilizes a rejection-oriented prediction, "
            "because appellate courts are slow to disturb well-supported findings."
        ),
    },
    "prior_conviction": {
        "keywords": ["previous conviction", "repeat offender", "criminal history", "habitual offender",
                     "prior record", "earlier case", "past crime"],
        "weight": 0.07,
        "direction": "rejected",
        "response": (
            "Prior record alone is not decisive, but it can make relief harder when the rest of the case "
            "already leans against the appellant."
        ),
    },
    "lower_court_error": {
        "keywords": ["lower court erred", "wrong application", "misapplication of law",
                     "incorrect interpretation", "trial court error", "high court failed",
                     "erroneous finding", "perverse finding"],
        "weight": 0.11,
        "direction": "accepted",
        "response": (
            "A concrete lower-court legal error is a meaningful appellate ground, especially where the "
            "judgment misapplies settled law or ignores material evidence."
        ),
    },
    "delay": {
        "keywords": ["delay in filing", "limitation", "barred by time", "filed late",
                     "after limitation period", "time barred", "inordinate delay"],
        "weight": 0.09,
        "direction": "rejected",
        "response": (
            "Delay and limitation issues are serious procedural obstacles and often reinforce a rejection "
            "unless the delay is convincingly explained."
        ),
    },
    "constitutional_rights": {
        "keywords": ["article 21", "fundamental right", "right to life", "article 14",
                     "right to equality", "article 19", "freedom", "constitutional violation",
                     "due process"],
        "weight": 0.13,
        "direction": "accepted",
        "response": (
            "Constitutional-rights arguments are among the strongest grounds available because they attack "
            "the legal validity of the process itself."
        ),
    },
    "fresh_evidence": {
        "keywords": ["new evidence", "fresh evidence", "discovered later", "not available before",
                     "new witness", "recently found", "additional proof"],
        "weight": 0.10,
        "direction": "accepted",
        "response": (
            "Fresh evidence can matter, but courts usually expect it to be genuinely new, material, and "
            "not something that could have been produced earlier with diligence."
        ),
    },
}


class ArgumentSimulator:
    def _relevant_cases(self, similar_cases: list[dict[str, Any]], direction: str) -> list[dict[str, Any]]:
        label = "ACCEPTED" if direction == "accepted" else "REJECTED"
        return [case for case in similar_cases if case.get("label") == label]

    def _cases_summary(self, cases: list[dict[str, Any]], limit: int = 2) -> str:
        if not cases:
            return ""
        snippets = []
        for case in cases[:limit]:
            reason = case.get("match_reasons") or []
            if reason:
                snippets.append(reason[0])
            else:
                snippets.append(f"{case.get('label', 'UNKNOWN')} case at {case.get('similarity', 0):.2f} similarity")
        return "; ".join(snippets)

    def _rules_summary(self, current_rules: list[dict[str, Any]], preferred_direction: str) -> str:
        matching = [rule["rule"] for rule in current_rules if rule.get("direction") == preferred_direction]
        if not matching:
            return ""
        return ", ".join(matching[:2])

    def _find_matching_pattern(self, argument_text: str):
        arg_lower = argument_text.lower()
        matched_category = None
        matched_pattern = None
        best_match_count = 0

        for category, pattern in ARGUMENT_PATTERNS.items():
            count = sum(1 for kw in pattern["keywords"] if kw in arg_lower)
            if count > best_match_count:
                best_match_count = count
                matched_category = category
                matched_pattern = pattern

        return matched_category, matched_pattern, best_match_count

    def analyze_argument(
        self,
        argument_text: str,
        current_verdict: str,
        current_confidence: float,
        similar_cases: list,
        round_number: int,
        current_rules: list | None = None,
        top_keywords: list | None = None,
    ) -> dict:
        current_rules = current_rules or []
        top_keywords = top_keywords or []

        total = len([case for case in similar_cases if case.get("label") in {"ACCEPTED", "REJECTED"}])
        sim_accepted = sum(1 for c in similar_cases if c.get("label") == "ACCEPTED")
        sim_rejected = sum(1 for c in similar_cases if c.get("label") == "REJECTED")

        matched_category, matched_pattern, best_match_count = self._find_matching_pattern(argument_text)

        if matched_pattern is None or best_match_count == 0:
            return self._generic_response(
                argument_text,
                current_verdict,
                current_confidence,
                sim_accepted,
                sim_rejected,
                total,
                round_number,
                top_keywords,
            )

        direction = matched_pattern["direction"]
        weight = matched_pattern["weight"]

        supporting_cases = self._relevant_cases(similar_cases, direction)
        opposing_cases = self._relevant_cases(similar_cases, "rejected" if direction == "accepted" else "accepted")
        support_case_factor = min(len(supporting_cases), 3) * 0.01
        oppose_case_factor = min(len(opposing_cases), 3) * 0.008

        rules_bias = 0.0
        if self._rules_summary(current_rules, direction):
            rules_bias += 0.015
        if self._rules_summary(current_rules, "rejected" if direction == "accepted" else "accepted"):
            rules_bias -= 0.015

        diminish_factor = max(0.45, 1.0 - (round_number - 1) * 0.12)
        effective_weight = max(0.03, weight * diminish_factor + support_case_factor - oppose_case_factor + rules_bias)

        if direction == "accepted":
            if current_verdict == "REJECTED":
                new_confidence = current_confidence - effective_weight
                confidence_shift = -effective_weight
            else:
                new_confidence = min(current_confidence + effective_weight * 0.45, 0.92)
                confidence_shift = effective_weight * 0.45
        else:
            if current_verdict == "ACCEPTED":
                new_confidence = current_confidence - effective_weight
                confidence_shift = -effective_weight
            else:
                new_confidence = min(current_confidence + effective_weight * 0.45, 0.92)
                confidence_shift = effective_weight * 0.45

        new_confidence = max(0.40, min(new_confidence, 0.92))
        new_verdict = current_verdict

        if current_verdict == "REJECTED" and new_confidence < 0.50:
            new_verdict = "ACCEPTED"
            new_confidence = 0.53
        elif current_verdict == "ACCEPTED" and new_confidence < 0.50:
            new_verdict = "REJECTED"
            new_confidence = 0.53

        ai_response_parts = [matched_pattern["response"]]

        if supporting_cases:
            ai_response_parts.append(
                f"Retrieved support is not abstract: {len(supporting_cases)} similar "
                f"{'accepted' if direction == 'accepted' else 'rejected'} cases align with this argument "
                f"({self._cases_summary(supporting_cases)})."
            )
        elif total:
            ai_response_parts.append(
                "The argument is legally relevant, but the currently retrieved precedents do not strongly reinforce it."
            )

        matching_rules = self._rules_summary(current_rules, direction)
        if matching_rules:
            ai_response_parts.append(
                f"The current prediction already carries rule signals in the same direction, including {matching_rules}."
            )

        if opposing_cases and current_verdict != ("ACCEPTED" if direction == "accepted" else "REJECTED"):
            ai_response_parts.append(
                f"However, the present prediction is still anchored by opposing precedents "
                f"({self._cases_summary(opposing_cases)})."
            )

        if new_verdict != current_verdict:
            ai_response_parts.append(
                f"Overall, this argument is strong enough to shift the system from {current_verdict} to {new_verdict}."
            )
        else:
            shift_pct = abs(confidence_shift) * 100
            if confidence_shift < 0:
                ai_response_parts.append(
                    f"Net effect: confidence in the {current_verdict} prediction drops by about {shift_pct:.1f}%."
                )
            else:
                ai_response_parts.append(
                    f"Net effect: confidence in the {current_verdict} prediction rises by about {shift_pct:.1f}%."
                )

        evidence_points = []
        if supporting_cases:
            evidence_points.append(
                f"{len(supporting_cases)} retrieved cases move in the same direction as this argument."
            )
        if matching_rules:
            evidence_points.append(f"Supporting rule signals: {matching_rules}.")
        if top_keywords:
            top_words = [kw["word"] for kw in top_keywords[:3] if "word" in kw]
            if top_words:
                evidence_points.append(f"Current model focus terms include: {', '.join(top_words)}.")

        return {
            "updated_verdict": new_verdict,
            "updated_confidence": round(new_confidence, 4),
            "ai_response": " ".join(ai_response_parts),
            "argument_category": matched_category.replace("_", " ").title(),
            "confidence_shift": round(confidence_shift, 4),
            "verdict_changed": new_verdict != current_verdict,
            "evidence_points": evidence_points,
        }

    def _generic_response(
        self,
        argument: str,
        verdict: str,
        confidence: float,
        sim_accepted: int,
        sim_rejected: int,
        total: int,
        round_number: int,
        top_keywords: list[dict[str, Any]],
    ):
        focus_words = ", ".join(kw["word"] for kw in top_keywords[:3] if "word" in kw) if top_keywords else ""
        responses = [
            (
                f"Your argument raises a relevant point, but it is still too general to materially move the prediction. "
                f"Among the currently retrieved cases, the split is {sim_accepted} accepted and {sim_rejected} rejected "
                f"out of {total}. Add a statute, procedural defect, evidentiary weakness, or constitutional ground."
            ),
            (
                f"This argument needs stronger legal grounding. The current prediction remains {verdict} with "
                f"{confidence * 100:.1f}% confidence. Try connecting the argument to specific legal issues already visible "
                f"in the case, such as {focus_words or 'the key model terms'}."
            ),
            (
                f"The simulator has noted the point, but it does not yet outweigh the present evidence profile. "
                f"To shift the result, make the argument more concrete and precedent-oriented."
            ),
        ]

        idx = min(round_number - 1, len(responses) - 1)
        return {
            "updated_verdict": verdict,
            "updated_confidence": confidence,
            "ai_response": responses[idx],
            "argument_category": "General",
            "confidence_shift": 0.0,
            "verdict_changed": False,
            "evidence_points": [
                f"Retrieved case split: {sim_accepted} accepted vs {sim_rejected} rejected."
            ] if total else [],
        }
