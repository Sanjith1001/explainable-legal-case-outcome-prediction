"""
FastAPI Backend — Main Server v3
6-layer architecture + Legal Argument Simulator
Run: .venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback
import io
import os
import sys

from backend.predictor   import Predictor
from backend.retriever   import Retriever
from backend.explainer   import Explainer
from backend.legal_rules import LegalRuleEngine
from backend.simulator   import ArgumentSimulator


def ensure_running_in_project_venv() -> None:
    """Fail fast if backend is started outside this repository's virtualenv."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    venv_python = os.path.join(project_root, ".venv", "Scripts", "python.exe")
    current_python = os.path.abspath(sys.executable)

    if not os.path.exists(venv_python):
        raise RuntimeError(
            "Project virtual environment not found at '.venv\\Scripts\\python.exe'. "
            "Create it with: py -m venv .venv"
        )

    if os.path.normcase(current_python) != os.path.normcase(venv_python):
        raise RuntimeError(
            "Backend must run from the project virtual environment only.\n"
            "Use: .venv\\Scripts\\python -m uvicorn backend.main:app --reload --port 8000"
        )


ensure_running_in_project_venv()

app = FastAPI(title="Explainable Legal Case Outcome Predictor v3", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading models...")
predictor  = Predictor()
retriever  = Retriever()
explainer  = Explainer(predictor.tfidf, predictor.model)
rule_engine = LegalRuleEngine()
simulator  = ArgumentSimulator()
print("All models loaded. Server ready.")


# ── Schemas ────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    case_text: str

class SimulateRequest(BaseModel):
    argument      : str
    current_verdict    : str
    current_confidence : float
    similar_cases      : list
    round_number       : int = 1
    current_rules      : list[dict] = []
    top_keywords       : list[dict] = []

class SimilarCase(BaseModel):
    text_snippet : str
    label        : str
    similarity   : float
    semantic_score: float | None = None
    lexical_score: float | None = None
    source       : str | None = None
    source_name  : str | None = None
    match_reasons: list[str] = []
    document_url : str | None = None

class PredictResponse(BaseModel):
    verdict            : str
    confidence         : float
    confidence_band    : str
    label              : int
    top_keywords       : list[dict]
    similar_cases      : list[SimilarCase]
    explanation_text   : str
    explanation_points : list[str]
    explanation_sections: dict
    evidence_points    : list[str]
    triggered_rules    : list[dict]
    uncertainty_flag   : bool
    uncertainty_message: str
    consistency_status : str
    retrieval_strategy : str
    retrieval_sources  : list[str]

class SimulateResponse(BaseModel):
    updated_verdict    : str
    updated_confidence : float
    ai_response        : str
    argument_category  : str
    confidence_shift   : float
    verdict_changed    : bool
    evidence_points    : list[str]


# ── PDF extraction ─────────────────────────────────────────────
def extract_pdf_text(pdf_bytes: bytes) -> str:
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        text   = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except ImportError:
        raise HTTPException(status_code=500,
            detail="Install pypdf in .venv: .venv\\Scripts\\pip install pypdf")
    except Exception as e:
        raise HTTPException(status_code=400,
            detail=f"PDF read error: {str(e)}")


# ── Rich explanation builder ───────────────────────────────────
def get_confidence_band(confidence: float) -> str:
    if confidence >= 0.82:
        return "high"
    if confidence >= 0.67:
        return "moderate"
    if confidence >= 0.55:
        return "low"
    return "uncertain"


def build_explanation(verdict, confidence, keywords, similar_cases,
                      raw_prob, triggered_rules):
    pct            = round(confidence * 100, 1)
    accepted_count = sum(1 for c in similar_cases if c["label"] == "ACCEPTED")
    rejected_count = len(similar_cases) - accepted_count
    total          = len(similar_cases)

    seen       = set()
    support_kw = []
    against_kw = []
    all_kw     = []
    for k in keywords:
        w = k["word"]
        if w in seen: continue
        seen.add(w)
        all_kw.append(w)
        if k["direction"] == "supports_accepted": support_kw.append(w)
        else: against_kw.append(w)

    conf_desc = get_confidence_band(confidence)
    conf_desc_text = "strong" if conf_desc == "high" else conf_desc

    if accepted_count == total:
        prec = f"All {total} similar past cases were ACCEPTED."
    elif rejected_count == total:
        prec = f"All {total} similar past cases were REJECTED."
    elif accepted_count > rejected_count:
        prec = f"{accepted_count} of {total} similar past cases were ACCEPTED."
    elif rejected_count > accepted_count:
        prec = f"{rejected_count} of {total} similar past cases were REJECTED."
    else:
        prec = f"Similar past cases show mixed outcomes ({accepted_count} accepted, {rejected_count} rejected)."

    contradiction = ""
    if verdict == "ACCEPTED" and rejected_count > accepted_count:
        contradiction = (
            f" Note: While the model predicts acceptance, {rejected_count} of {total} "
            f"similar cases were rejected — indicating this is a borderline case."
        )
    elif verdict == "REJECTED" and accepted_count > rejected_count:
        contradiction = (
            f" Note: While the model predicts rejection, {accepted_count} of {total} "
            f"similar cases were accepted — this case may benefit from further legal review."
        )

    rule_note = ""
    if triggered_rules:
        accept_rules = [r["rule"] for r in triggered_rules if r["direction"] == "accepted"]
        reject_rules = [r["rule"] for r in triggered_rules if r["direction"] == "rejected"]
        if accept_rules:
            rule_note += f" Legal principles supporting acceptance: {', '.join(accept_rules[:2])}."
        if reject_rules:
            rule_note += f" Legal principles supporting rejection: {', '.join(reject_rules[:2])}."

    prob_note = f"The model assigned {round(raw_prob*100,1)}% probability of acceptance."

    if verdict == "ACCEPTED":
        kw_note = (
            f"Key legal terms supporting this prediction: {', '.join(support_kw[:3])}."
            if support_kw else
            f"Key legal factors: {', '.join(all_kw[:3])}."
        )
    else:
        kw_note = (
            f"Key legal terms suggesting rejection: {', '.join(against_kw[:3])}."
            if against_kw else
            f"Key legal factors: {', '.join(all_kw[:3])}."
        )

    summary = (
        f"The AI model predicts this case will be {verdict} with {conf_desc_text} confidence ({pct}%). "
        f"{kw_note} {prob_note} {prec}{rule_note}{contradiction}"
    )

    explanation_points = [
        f"Predicted outcome: {verdict} with {pct}% confidence ({conf_desc} band).",
        kw_note,
        prob_note,
        prec,
    ]
    if rule_note:
        explanation_points.append(rule_note.strip())
    if contradiction:
        explanation_points.append(contradiction.strip())

    explanation_sections = {
        "prediction": f"{verdict} ({pct}% confidence, {conf_desc} band)",
        "keywords": support_kw[:3] if verdict == "ACCEPTED" else against_kw[:3],
        "similar_cases_summary": prec,
        "rules_summary": rule_note.strip(),
        "contradiction_note": contradiction.strip(),
        "raw_probability_accepted": round(raw_prob * 100, 1),
    }

    return summary, explanation_points, explanation_sections


# ── Core prediction pipeline (6 layers) ───────────────────────
def run_prediction(text: str):
    if len(text.strip()) < 50:
        raise HTTPException(status_code=400,
            detail="Minimum 50 characters required.")

    # Layer 1: ML Prediction
    label, confidence, proba = predictor.predict_with_proba(text)
    raw_prob_accepted = float(proba[1])

    # Layer 2: Semantic Retrieval
    similar_cases = retriever.get_similar_cases(text, top_k=5)

    # Layer 3: SHAP Explainability
    top_keywords = explainer.explain(text, top_n=10)

    # Layer 4: Legal Rule Engine
    rule_result      = rule_engine.apply_rules(text, raw_prob_accepted)
    adjusted_prob    = rule_result["adjusted_prob_accepted"]
    triggered_rules  = rule_result["triggered_rules"]

    # Re-decide label based on rule-adjusted probability
    from backend.predictor import ACCEPT_THRESHOLD
    label      = 1 if adjusted_prob >= ACCEPT_THRESHOLD else 0
    confidence = min(adjusted_prob if label == 1 else (1 - adjusted_prob), 0.92)

    # Layer 5: Consistency Checker
    sim_accepted = sum(1 for c in similar_cases if c["label"] == "ACCEPTED")
    sim_rejected = len(similar_cases) - sim_accepted

    if sim_accepted >= 4 and label == 0:
        label      = 1
        confidence = max(float(proba[1]), 0.58)
    elif sim_rejected >= 4 and label == 1:
        label      = 0
        confidence = max(float(proba[0]), 0.58)
    elif sim_accepted >= 3 and label == 0 and raw_prob_accepted > 0.28:
        label      = 1
        confidence = max(float(proba[1]), 0.55)

    confidence = min(confidence, 0.92)
    confidence_band = get_confidence_band(confidence)

    if sim_accepted == sim_rejected:
        consistency_status = "Mixed — similar cases show equal split"
    elif (sim_accepted > sim_rejected and label == 1) or (sim_rejected > sim_accepted and label == 0):
        consistency_status = "Consistent — prediction aligns with similar cases"
    else:
        consistency_status = "Inconsistent — prediction differs from similar case majority"

    # Layer 6: Uncertainty Detector
    uncertainty_flag    = confidence < 0.60
    uncertainty_message = ""
    if uncertainty_flag:
        uncertainty_message = (
            f"Low confidence ({confidence*100:.1f}%) — This is a borderline case. "
            f"We recommend consulting a legal expert before relying on this prediction. "
            f"Use the Argument Simulator below to explore how different legal arguments "
            f"might affect the outcome."
        )

    verdict = "ACCEPTED" if label == 1 else "REJECTED"

    explanation_text, explanation_points, explanation_sections = build_explanation(
        verdict, confidence, top_keywords,
        similar_cases, raw_prob_accepted, triggered_rules
    )

    evidence_points = []
    if top_keywords:
        evidence_points.append(
            "Top model terms: " + ", ".join(k["word"] for k in top_keywords[:3])
        )
    if similar_cases:
        local_cases = [c for c in similar_cases if c.get("source") == "local_corpus"]
        if local_cases:
            evidence_points.append(
                f"{min(len(local_cases), 5)} retrieved local precedents contributed to the explanation."
            )
        for case in local_cases[:2]:
            reasons = case.get("match_reasons") or []
            if reasons:
                evidence_points.append(f"Retrieved case signal: {reasons[0]}.")
    if triggered_rules:
        evidence_points.append(
            "Triggered rules: " + ", ".join(rule["rule"] for rule in triggered_rules[:3])
        )

    retrieval_sources = sorted({
        case.get("source_name") or case.get("source") or "Unknown source"
        for case in similar_cases
    })

    return PredictResponse(
        verdict             = verdict,
        confidence          = round(confidence, 4),
        confidence_band     = confidence_band,
        label               = label,
        top_keywords        = top_keywords,
        similar_cases       = similar_cases,
        explanation_text    = explanation_text,
        explanation_points  = explanation_points,
        explanation_sections= explanation_sections,
        evidence_points     = evidence_points,
        triggered_rules     = triggered_rules,
        uncertainty_flag    = uncertainty_flag,
        uncertainty_message = uncertainty_message,
        consistency_status  = consistency_status,
        retrieval_strategy  = "hybrid_semantic_lexical_with_optional_external_enrichment",
        retrieval_sources   = retrieval_sources,
    )


# ── Routes ─────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Legal AI v3 running — 6 layers active"}

@app.get("/health")
def health():
    return {"status": "ok", "version": "3.0"}

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    try:
        return run_prediction(request.case_text)
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-pdf", response_model=PredictResponse)
async def predict_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF supported.")
        pdf_bytes = await file.read()
        text      = extract_pdf_text(pdf_bytes)
        if len(text.strip()) < 50:
            raise HTTPException(status_code=400,
                detail="PDF has insufficient text. Ensure it is text-based, not scanned.")
        return run_prediction(text)
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/simulate", response_model=SimulateResponse)
def simulate(request: SimulateRequest):
    try:
        if len(request.argument.strip()) < 10:
            raise HTTPException(status_code=400,
                detail="Please provide a more detailed argument (minimum 10 characters).")
        result = simulator.analyze_argument(
            argument_text      = request.argument,
            current_verdict    = request.current_verdict,
            current_confidence = request.current_confidence,
            similar_cases      = request.similar_cases,
            round_number       = request.round_number,
            current_rules      = request.current_rules,
            top_keywords       = request.top_keywords,
        )
        return SimulateResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
