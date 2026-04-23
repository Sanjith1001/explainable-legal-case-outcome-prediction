# Case Outcome Predictor Documentation

## 1. Project Overview

Case Outcome Predictor is an explainable legal AI application for predicting Indian Supreme Court case outcomes. The system accepts case text, predicts whether the case is likely to be `ACCEPTED` or `REJECTED`, and returns supporting explanations such as key legal factors, similar past cases, legal rule triggers, uncertainty notes, and consistency checks.

The project has two main parts:

- `backend/`: FastAPI service that loads trained models and exposes prediction APIs.
- `frontend/`: React application that lets users paste case text and view the prediction results.

The backend uses a six-layer prediction architecture:

1. TF-IDF + XGBoost classification
2. FAISS semantic retrieval of similar cases
3. SHAP keyword-level explainability
4. Legal rule-based probability adjustment
5. Similar-case consistency checking
6. Low-confidence uncertainty detection

There is also an argument simulator API that evaluates lawyer-style arguments and estimates whether those arguments shift the predicted verdict.

## 2. Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn
- Pandas and NumPy
- scikit-learn
- XGBoost
- Sentence Transformers
- FAISS
- SHAP
- Pydantic

### Frontend

- React 18
- Axios
- Create React App

### Machine Learning

- Classifier: XGBoost binary classifier
- Text features: TF-IDF with unigrams, bigrams, and trigrams
- Semantic retrieval embeddings: `law-ai/InLegalBERT`
- Vector search: FAISS `IndexFlatIP`
- Explainability: SHAP `TreeExplainer`

## 3. Repository Structure

```text
Case Outcome Predictor/
|-- backend/
|   |-- main.py              # FastAPI app, routes, prediction pipeline
|   |-- predictor.py         # TF-IDF + XGBoost prediction wrapper
|   |-- retriever.py         # FAISS + InLegalBERT similar-case retrieval
|   |-- explainer.py         # SHAP keyword explanation engine
|   |-- legal_rules.py       # Legal rule engine for probability adjustment
|   |-- simulator.py         # Argument simulator
|   `-- __init__.py
|-- data/
|   `-- get_ildc.py          # Dataset download helper
|-- frontend/
|   |-- public/
|   |-- src/
|   |   |-- App.jsx
|   |   |-- index.js
|   |   |-- index.css
|   |   `-- components/
|   |       |-- CaseInput.jsx
|   |       |-- VerdictCard.jsx
|   |       |-- KeywordsPanel.jsx
|   |       |-- SimilarCases.jsx
|   |       |-- Navbar.jsx
|   |       |-- LoadingSpinner.jsx
|   |       `-- ErrorBoundary.jsx
|   |-- package.json
|   `-- README.md
|-- models/
|   |-- xgboost_model.pkl
|   |-- tfidf_vectorizer.pkl
|   |-- faiss_index.bin
|   `-- case_store.pkl
|-- merge_datasets.py        # Merges ILDC and original legal dataset
|-- preprocess_and_train.py  # Cleans data, trains model, builds FAISS index
|-- requirements.txt
`-- PROJECT_DOCUMENTATION.md
```

## 4. Backend Architecture

The backend entry point is `backend/main.py`.

When the server starts, it loads:

- `Predictor`: TF-IDF vectorizer and XGBoost model
- `Retriever`: FAISS index, case store, and InLegalBERT embedding model
- `Explainer`: SHAP explainer for the XGBoost model
- `LegalRuleEngine`: rule-based legal probability adjuster
- `ArgumentSimulator`: argument analysis and counter-response engine

### Prediction Flow

The main prediction pipeline is implemented in `run_prediction(text)`.

1. Validate that the input has at least 50 characters.
2. Run base model prediction using `Predictor.predict_with_proba`.
3. Retrieve top 5 similar cases using FAISS semantic search.
4. Generate top SHAP keywords from the current case.
5. Apply legal rules to adjust the accepted-case probability.
6. Recompute the final label using the calibrated accept threshold.
7. Compare prediction with the majority result among similar cases.
8. Flag uncertainty if confidence is below 60%.
9. Build a human-readable explanation.
10. Return a structured API response.

### Class Labels

The project uses binary labels:

- `1`: `ACCEPTED`
- `0`: `REJECTED`

The calibrated accept threshold is defined in `backend/predictor.py`:

```python
ACCEPT_THRESHOLD = 0.38
```

This threshold is lower than `0.5` to counter class imbalance in the training data.

## 5. Backend API Documentation

Default backend URL:

```text
http://localhost:8000
```

Run the backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

FastAPI also provides automatic interactive docs at:

```text
http://localhost:8000/docs
```

### GET `/`

Health-style root endpoint.

Response:

```json
{
  "message": "Legal AI v3 running - 6 layers active"
}
```

### GET `/health`

Checks whether the API is running.

Response:

```json
{
  "status": "ok",
  "version": "3.0"
}
```

### POST `/predict`

Predicts a case outcome from raw text.

Request body:

```json
{
  "case_text": "Full case facts, arguments, judgment, or petition text..."
}
```

Validation:

- `case_text` must contain at least 50 characters.

Response body:

```json
{
  "verdict": "ACCEPTED",
  "confidence": 0.7421,
  "label": 1,
  "top_keywords": [
    {
      "word": "constitutional",
      "shap_value": 0.1832,
      "direction": "supports_accepted"
    }
  ],
  "similar_cases": [
    {
      "text_snippet": "Case excerpt...",
      "label": "ACCEPTED",
      "similarity": 0.8123
    }
  ],
  "explanation_text": "The AI model predicts this case will be ACCEPTED...",
  "triggered_rules": [
    {
      "rule": "Constitutional rights",
      "note": "Constitutional rights violation detected",
      "direction": "accepted",
      "weight": 0.08
    }
  ],
  "uncertainty_flag": false,
  "uncertainty_message": "",
  "consistency_status": "Consistent - prediction aligns with similar cases"
}
```

Example using `curl`:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d "{\"case_text\":\"The appellant contends that the High Court failed to consider the violation of Article 21 and procedural irregularities during arrest...\"}"
```

### POST `/predict-pdf`

Predicts an outcome from an uploaded PDF.

Request:

- Multipart form upload
- Field name: `file`
- File type: `.pdf`

Example using `curl`:

```bash
curl -X POST http://localhost:8000/predict-pdf \
  -F "file=@case.pdf"
```

Notes:

- The PDF must contain extractable text.
- Scanned image-only PDFs are not supported unless OCR is added.
- The endpoint imports `pypdf` dynamically. If PDF upload fails with a missing dependency error, install it with `pip install pypdf`.

### POST `/simulate`

Analyzes a legal argument against or in support of the current prediction.

Request body:

```json
{
  "argument": "The accused was not present at the scene and the alibi is supported by independent witnesses.",
  "current_verdict": "REJECTED",
  "current_confidence": 0.68,
  "similar_cases": [
    {
      "text_snippet": "Previous case excerpt...",
      "label": "ACCEPTED",
      "similarity": 0.79
    }
  ],
  "round_number": 1
}
```

Response body:

```json
{
  "updated_verdict": "REJECTED",
  "updated_confidence": 0.6,
  "ai_response": "Alibi evidence is a significant factor...",
  "argument_category": "Alibi",
  "confidence_shift": -0.08,
  "verdict_changed": false
}
```

Recognized argument categories include:

- Alibi
- Procedural violation
- Weak evidence
- Benefit of doubt
- Strong evidence
- Prior conviction
- Lower court error
- Delay
- Constitutional rights
- Fresh evidence

## 6. Frontend Documentation

The frontend is located in `frontend/`.

Run the frontend:

```bash
cd frontend
npm install
npm start
```

Default frontend URL:

```text
http://localhost:3000
```

The React app currently supports:

- Text input for case facts, arguments, or judgment text
- Minimum input validation of 50 characters
- Prediction request to `http://localhost:8000/predict`
- Verdict display with confidence bar
- Generated explanation text
- SHAP keyword panel
- Similar past cases panel
- Reset action for analyzing another case

The frontend package has this proxy configured:

```json
"proxy": "http://localhost:8000"
```

However, `App.jsx` currently calls the backend using the absolute URL `http://localhost:8000/predict`.

## 7. Model Training Pipeline

The training pipeline is implemented in `preprocess_and_train.py`.

Run it from the project root:

```bash
python preprocess_and_train.py
```

The script expects:

```text
data/final_dataset.csv
```

with at least these columns:

```text
text,label
```

### Training Steps

1. Load `data/final_dataset.csv`.
2. Drop rows with missing `text` or `label`.
3. Extract legally relevant text sections based on markers such as `facts`, `held`, `judgment`, `appeal`, `appellant`, and `respondent`.
4. Clean text by removing URLs, citation artifacts, dates, pure numbers, and unusual characters.
5. Remove very short records.
6. Split into train/test sets with stratification.
7. Fit a TF-IDF vectorizer with up to 20,000 features and 1-3 word ngrams.
8. Train an XGBoost binary classifier.
9. Evaluate with default and calibrated thresholds.
10. Save the model and vectorizer.
11. Generate InLegalBERT embeddings.
12. Normalize embeddings and build a FAISS index.
13. Save the FAISS index and case store.

### Generated Artifacts

The training script writes:

```text
models/tfidf_vectorizer.pkl
models/xgboost_model.pkl
models/faiss_index.bin
models/case_store.pkl
```

These files are required by the backend at startup.

## 8. Dataset Preparation

`merge_datasets.py` combines:

- ILDC split files:
  - `data/ildc_multi_train.csv`
  - `data/ildc_single_dev.csv`
  - `data/ildc_test.csv`
- Original legal dataset:
  - `data/legal_cases_dataset.csv`

It produces:

```text
data/final_dataset.csv
```

The merge script maps the original dataset labels as:

- `-1` to `0`
- `1` to `1`
- Drops neutral `0`

Then it shuffles the combined dataset using `random_state=42`.

## 9. Setup Instructions

### Backend Setup

Create and activate a Python environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Optional PDF dependency:

```bash
pip install pypdf
```

Start the backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Open:

```text
http://localhost:3000
```

## 10. Environment and Runtime Notes

- The backend must be started from the project root so relative paths like `models/xgboost_model.pkl` resolve correctly.
- The first backend startup may take time because `SentenceTransformer("law-ai/InLegalBERT")` needs to load the embedding model.
- If the embedding model is not cached locally, the environment needs network access to download it.
- The backend allows all CORS origins with `allow_origins=["*"]`, which is convenient for development but should be restricted in production.
- Model confidence is capped at `0.92` because absolute certainty is unrealistic in legal prediction.
- The system is decision-support software, not a substitute for legal advice.

## 11. Legal Rule Engine

The rule engine is implemented in `backend/legal_rules.py`.

It detects legal patterns and adjusts the accepted-case probability. Examples:

| Rule | Direction | Weight |
| --- | --- | --- |
| Benefit of doubt | Accepted | 0.06 |
| Constitutional rights | Accepted | 0.08 |
| Procedural violation | Accepted | 0.07 |
| Strong forensic evidence | Rejected | 0.05 |
| Confession | Rejected | 0.07 |
| Acquittal appeal | Rejected | 0.05 |
| High court dismissed | Rejected | 0.04 |
| Delay / limitation | Rejected | 0.06 |

Each rule checks for keyword matches. Multiple hits can increase the adjustment, capped at two hits per rule.

## 12. Explainability

The system returns two kinds of explanation:

### SHAP Keywords

`backend/explainer.py` finds the most influential TF-IDF features present in the input text.

Each keyword includes:

- `word`: TF-IDF feature
- `shap_value`: contribution value
- `direction`: `supports_accepted` or `supports_rejected`

### Natural-Language Explanation

`build_explanation()` in `backend/main.py` combines:

- Final verdict
- Confidence score
- Raw accepted probability
- SHAP keywords
- Similar case outcome distribution
- Triggered legal rules
- Contradiction notes when similar cases disagree with the model

## 13. Similar Case Retrieval

`backend/retriever.py` performs semantic search.

Process:

1. Clean the query.
2. Truncate to the first 1,500 characters.
3. Embed the query using InLegalBERT.
4. Normalize the vector.
5. Search the FAISS index.
6. Return the top matching cases.

Each result contains:

- `text_snippet`: first 400 characters of the stored case
- `label`: `ACCEPTED` or `REJECTED`
- `similarity`: cosine-style similarity score

## 14. Production Considerations

Before deploying this project, consider:

- Restricting CORS origins.
- Moving hard-coded URLs into environment variables.
- Adding authentication if case text may be confidential.
- Removing secrets or tokens from source files.
- Adding OCR support for scanned PDFs.
- Adding tests for backend routes and model wrappers.
- Adding structured logging instead of relying on `print`.
- Pinning dependency versions in `requirements.txt`.
- Serving the frontend build from a production web server.
- Validating and monitoring model drift over time.

## 15. Common Commands

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Train models and build FAISS index:

```bash
python preprocess_and_train.py
```

Run backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

Run frontend:

```bash
cd frontend
npm start
```

Build frontend:

```bash
cd frontend
npm run build
```

## 16. Limitations

- Predictions depend on the quality and coverage of the training dataset.
- The rule engine is keyword-based and may miss legal meaning expressed differently.
- Similar-case retrieval uses only the first 1,500 characters of the query.
- PDF upload works only for text-based PDFs unless OCR is added.
- The frontend currently does not expose the `/simulate` and `/predict-pdf` endpoints.
- Legal predictions should be treated as assistive analysis, not authoritative legal advice.
