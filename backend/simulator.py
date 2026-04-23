"""
Legal Argument Simulator
Allows lawyers to challenge the AI prediction with arguments.
AI responds with counter-arguments based on legal rules + similar cases.
"""

import re
from typing import Optional

# ── Legal keywords → argument categories ──────────────────────
ARGUMENT_PATTERNS = {
    "alibi": {
        "keywords": ["alibi","was not present","not at scene","witness confirms absence","whereabouts"],
        "weight":    0.08,
        "direction": "accepted",
        "response":  "Alibi evidence is a significant factor. However, courts in India have held that "
                     "alibi must be proven beyond reasonable doubt by the accused (Section 103 IEA). "
                     "In {similar_accepted} of {total} similar cases with alibi claims, courts accepted "
                     "the appeal when the alibi was corroborated by independent witnesses."
    },
    "procedural_violation": {
        "keywords": ["procedure not followed","violated","illegal arrest","section 50 crpc",
                     "rights violated","not informed","no warrant","illegal search"],
        "weight":    0.10,
        "direction": "accepted",
        "response":  "Procedural violations are a strong ground for appeal. The Supreme Court has "
                     "consistently held that evidence obtained through illegal means may be inadmissible. "
                     "In {similar_accepted} of {total} similar cases citing procedural violation, "
                     "courts ruled in favour of the appellant."
    },
    "weak_evidence": {
        "keywords": ["weak evidence","no direct evidence","circumstantial only","insufficient proof",
                     "no eyewitness","unreliable witness","contradictory testimony","hearsay"],
        "weight":    0.09,
        "direction": "accepted",
        "response":  "Insufficiency of evidence is a valid ground. Courts apply the standard of "
                     "'proof beyond reasonable doubt'. Where evidence is purely circumstantial, "
                     "the chain must be complete and consistent only with guilt. "
                     "In {similar_accepted} of {total} similar cases with weak evidence arguments, "
                     "the benefit of doubt was extended to the appellant."
    },
    "benefit_of_doubt": {
        "keywords": ["benefit of doubt","reasonable doubt","not proven beyond","doubt exists",
                     "probability of innocence","cannot be certain"],
        "weight":    0.12,
        "direction": "accepted",
        "response":  "Benefit of doubt is a foundational principle in Indian criminal law. "
                     "The Supreme Court has repeatedly held that if two views are possible, "
                     "the one favouring the accused must be accepted. "
                     "This argument carries significant legal weight in {similar_accepted} of "
                     "{total} similar retrieved cases."
    },
    "strong_evidence": {
        "keywords": ["strong evidence","direct evidence","eyewitness","forensic proof",
                     "dna match","fingerprint","cctv","caught red handed","confession"],
        "weight":    0.10,
        "direction": "rejected",
        "response":  "Strong direct evidence significantly reduces the chance of appeal success. "
                     "Courts give high weight to forensic and eyewitness testimony. "
                     "In {similar_rejected} of {total} similar cases with strong evidence, "
                     "the conviction was upheld."
    },
    "prior_conviction": {
        "keywords": ["previous conviction","repeat offender","criminal history","habitual offender",
                     "prior record","earlier case","past crime"],
        "weight":    0.07,
        "direction": "rejected",
        "response":  "Prior criminal record is considered by courts while deciding appeals, "
                     "though it cannot be the sole basis. Courts have noted that habitual offenders "
                     "face a higher bar for relief. This factor is noted in {similar_rejected} of "
                     "{total} similar cases."
    },
    "lower_court_error": {
        "keywords": ["lower court erred","wrong application","misapplication of law",
                     "incorrect interpretation","trial court error","high court failed",
                     "erroneous finding","perverse finding"],
        "weight":    0.11,
        "direction": "accepted",
        "response":  "Errors in lower court judgments are valid grounds for Supreme Court intervention. "
                     "The Supreme Court can correct perverse findings of fact and errors of law. "
                     "In {similar_accepted} of {total} similar cases citing lower court error, "
                     "the appeal was accepted."
    },
    "delay": {
        "keywords": ["delay in filing","limitation","barred by time","filed late",
                     "after limitation period","time barred","inordinate delay"],
        "weight":    0.09,
        "direction": "rejected",
        "response":  "Delay and laches are serious procedural hurdles. Courts have held that "
                     "unexplained delay weakens the appellant's case. "
                     "In {similar_rejected} of {total} similar cases with delay issues, "
                     "the appeal was dismissed on limitation grounds."
    },
    "constitutional_rights": {
        "keywords": ["article 21","fundamental right","right to life","article 14",
                     "right to equality","article 19","freedom","constitutional violation",
                     "due process"],
        "weight":    0.13,
        "direction": "accepted",
        "response":  "Constitutional rights violations are the strongest grounds for appeal. "
                     "The Supreme Court acts as guardian of fundamental rights under Article 32. "
                     "In {similar_accepted} of {total} similar cases involving constitutional rights, "
                     "courts intervened in favour of the appellant."
    },
    "fresh_evidence": {
        "keywords": ["new evidence","fresh evidence","discovered later","not available before",
                     "new witness","recently found","additional proof"],
        "weight":    0.10,
        "direction": "accepted",
        "response":  "Fresh evidence can be a ground for review/recall of judgment. However, "
                     "courts apply strict scrutiny — evidence must be genuine, relevant and "
                     "could not have been produced earlier with due diligence. "
                     "In {similar_accepted} of {total} similar cases with fresh evidence, "
                     "courts admitted the appeal."
    },
}

# ── Argument analyzer ──────────────────────────────────────────
class ArgumentSimulator:

    def analyze_argument(
        self,
        argument_text: str,
        current_verdict: str,
        current_confidence: float,
        similar_cases: list,
        round_number: int,
    ) -> dict:
        """
        Analyzes lawyer's argument and returns:
        - updated_verdict
        - updated_confidence
        - ai_response (detailed legal counter-argument)
        - argument_category (what type of argument was detected)
        - confidence_shift (how much confidence changed)
        - legal_basis (the law/principle cited)
        """

        arg_lower    = argument_text.lower()
        total        = len(similar_cases)
        sim_accepted = sum(1 for c in similar_cases if c["label"] == "ACCEPTED")
        sim_rejected = total - sim_accepted

        # Find matching argument pattern
        matched_category = None
        matched_pattern  = None
        best_match_count = 0

        for category, pattern in ARGUMENT_PATTERNS.items():
            count = sum(1 for kw in pattern["keywords"] if kw in arg_lower)
            if count > best_match_count:
                best_match_count = count
                matched_category = category
                matched_pattern  = pattern

        # Default response if no pattern matched
        if matched_pattern is None or best_match_count == 0:
            return self._generic_response(
                argument_text, current_verdict,
                current_confidence, sim_accepted,
                sim_rejected, total, round_number
            )

        # Calculate confidence shift
        direction = matched_pattern["direction"]
        weight    = matched_pattern["weight"]

        # Diminishing returns on repeated arguments
        diminish_factor = max(0.4, 1.0 - (round_number - 1) * 0.15)
        effective_weight = weight * diminish_factor

        if direction == "accepted":
            if current_verdict == "REJECTED":
                # Argument pushes against current prediction
                new_confidence = current_confidence - effective_weight
                confidence_shift = -effective_weight
            else:
                # Argument supports current prediction
                new_confidence   = min(current_confidence + effective_weight * 0.5, 0.92)
                confidence_shift = effective_weight * 0.5
        else:
            if current_verdict == "ACCEPTED":
                new_confidence   = current_confidence - effective_weight
                confidence_shift = -effective_weight
            else:
                new_confidence   = min(current_confidence + effective_weight * 0.5, 0.92)
                confidence_shift = effective_weight * 0.5

        # Check if verdict flips
        new_confidence  = max(0.45, min(new_confidence, 0.92))
        new_verdict     = current_verdict

        if current_verdict == "REJECTED" and new_confidence < 0.52:
            new_verdict    = "ACCEPTED"
            new_confidence = 0.54

        elif current_verdict == "ACCEPTED" and new_confidence < 0.52:
            new_verdict    = "REJECTED"
            new_confidence = 0.54

        # Format response
        ai_response = matched_pattern["response"].format(
            similar_accepted = sim_accepted,
            similar_rejected = sim_rejected,
            total            = total,
        )

        # Add verdict change note
        verdict_note = ""
        if new_verdict != current_verdict:
            verdict_note = (
                f" Based on this argument, the predicted outcome has shifted from "
                f"{current_verdict} to {new_verdict}."
            )
        else:
            shift_pct = abs(confidence_shift) * 100
            if confidence_shift < 0:
                verdict_note = (
                    f" This argument reduces confidence in the {current_verdict} prediction "
                    f"by {shift_pct:.1f}%."
                )
            else:
                verdict_note = (
                    f" This argument strengthens the {current_verdict} prediction "
                    f"by {shift_pct:.1f}%."
                )

        return {
            "updated_verdict"     : new_verdict,
            "updated_confidence"  : round(new_confidence, 4),
            "ai_response"         : ai_response + verdict_note,
            "argument_category"   : matched_category.replace("_", " ").title(),
            "confidence_shift"    : round(confidence_shift, 4),
            "verdict_changed"     : new_verdict != current_verdict,
        }

    def _generic_response(
        self, argument, verdict, confidence,
        sim_accepted, sim_rejected, total, round_number
    ):
        """Fallback response for unrecognized arguments."""
        responses = [
            f"Your argument raises a relevant point. However, based on analysis of {total} similar "
            f"cases ({sim_accepted} accepted, {sim_rejected} rejected), the model maintains its "
            f"prediction of {verdict}. To strengthen your position, consider citing specific legal "
            f"provisions, constitutional rights violations, or procedural irregularities.",

            f"This is a general argument that requires more specific legal grounding. Courts expect "
            f"arguments backed by statute, precedent, or established legal principles. "
            f"The current prediction remains {verdict} with {confidence*100:.1f}% confidence. "
            f"Try referencing specific IPC sections, CrPC provisions, or fundamental rights.",

            f"While this argument is noted, it lacks specific legal reference points that would "
            f"significantly influence the prediction. Consider arguing evidence insufficiency, "
            f"procedural violations, or constitutional rights to shift the outcome. "
            f"Current prediction: {verdict}.",
        ]

        idx = min(round_number - 1, len(responses) - 1)
        return {
            "updated_verdict"    : verdict,
            "updated_confidence" : confidence,
            "ai_response"        : responses[idx],
            "argument_category"  : "General",
            "confidence_shift"   : 0.0,
            "verdict_changed"    : False,
        }
