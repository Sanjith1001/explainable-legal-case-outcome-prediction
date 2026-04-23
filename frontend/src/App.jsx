import React, { useState } from 'react';
import axios from 'axios';
import Navbar from './components/Navbar';
import CaseInput from './components/CaseInput';
import VerdictCard from './components/VerdictCard';
import KeywordsPanel from './components/KeywordsPanel';
import SimilarCases from './components/SimilarCases';
import LoadingSpinner from './components/LoadingSpinner';

export default function App() {
  const [caseText, setCaseText] = useState('');
  const [inputMode, setInputMode] = useState('text');
  const [pdfFile,  setPdfFile]  = useState(null);
  const [result,   setResult]   = useState(null);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState('');

  const handlePredict = async () => {
    if (inputMode === 'text' && caseText.trim().length < 50) {
      setError('Please enter at least 50 characters of case text.');
      return;
    }
    if (inputMode === 'pdf' && !pdfFile) {
      setError('Please choose a PDF file to analyze.');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);
    try {
      let res;
      if (inputMode === 'pdf') {
        const formData = new FormData();
        formData.append('file', pdfFile);
        res = await axios.post('http://localhost:8000/predict-pdf', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      } else {
        res = await axios.post('http://localhost:8000/predict', {
          case_text: caseText,
        });
      }
      setResult(res.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Server error. Make sure the backend is running on port 8000.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setCaseText('');
    setPdfFile(null);
    setError('');
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f7f5f0' }}>
      <Navbar />

      <main style={{ maxWidth: '920px', margin: '0 auto', padding: '40px 20px 80px' }}>

        {/* Hero */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h2 style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: '40px',
            fontWeight: 700,
            color: '#0f1117',
            lineHeight: 1.2,
            marginBottom: '12px',
          }}>
            Explainable Legal Case<br />
            <span style={{ color: '#c9973a' }}>Outcome Prediction</span>
          </h2>
          <p style={{ color: '#9ca3af', fontSize: '14px', maxWidth: '500px', margin: '0 auto 16px' }}>
            Paste an Indian Supreme Court case and get an AI-powered prediction
            with SHAP explanations and semantically similar precedents.
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', flexWrap: 'wrap' }}>
            {['InLegalBERT', 'XGBoost', 'FAISS', 'SHAP', '45,868 Cases'].map(tag => (
              <span key={tag} style={{
                padding: '4px 12px',
                fontSize: '11px',
                fontFamily: 'DM Mono, monospace',
                background: '#ffffff',
                border: '1px solid #e5e1d8',
                borderRadius: '999px',
                color: '#9ca3af',
              }}>
                {tag}
              </span>
            ))}
          </div>
        </div>

        {/* Input */}
        <CaseInput
          caseText={caseText}
          setCaseText={setCaseText}
          inputMode={inputMode}
          setInputMode={setInputMode}
          pdfFile={pdfFile}
          setPdfFile={setPdfFile}
          onSubmit={handlePredict}
          loading={loading}
          error={error}
        />

        {/* Loading */}
        {loading && <LoadingSpinner />}

        {/* Results */}
        {result && !loading && (
          <div style={{ marginTop: '24px' }}>

            <VerdictCard
              verdict={result.verdict}
              confidence={result.confidence}
              explanationText={result.explanation_text}
            />

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
              gap: '24px',
              marginTop: '24px',
            }}>
              <KeywordsPanel keywords={result.top_keywords} />
              <SimilarCases  cases={result.similar_cases} />
            </div>

            <div style={{ textAlign: 'center', marginTop: '32px' }}>
              <button
                onClick={handleReset}
                style={{
                  padding: '10px 24px',
                  fontSize: '13px',
                  fontFamily: 'DM Mono, monospace',
                  background: '#ffffff',
                  border: '1px solid #d1cfc9',
                  borderRadius: '12px',
                  color: '#6b7280',
                  cursor: 'pointer',
                }}
              >
                Analyze Another Case
              </button>
            </div>
          </div>
        )}
      </main>

      <footer style={{
        textAlign: 'center',
        padding: '24px',
        fontSize: '11px',
        fontFamily: 'DM Mono, monospace',
        color: '#d1d5db',
        borderTop: '1px solid #e5e1d8',
      }}>
        Explainable Legal Case Outcome Prediction · IIIT Nagpur · 2025
      </footer>
    </div>
  );
}
