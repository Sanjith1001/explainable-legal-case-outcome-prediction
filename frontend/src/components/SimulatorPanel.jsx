import React, { useState } from 'react';
import axios from 'axios';

export default function SimulatorPanel({ result }) {
  const [argument, setArgument] = useState('');
  const [history, setHistory] = useState([]);
  const [state, setState] = useState({
    verdict: result.verdict,
    confidence: result.confidence,
    round: 1,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submitArgument = async () => {
    if (argument.trim().length < 10) {
      setError('Please provide a more detailed legal argument.');
      return;
    }

    setLoading(true);
    setError('');

    const lawyerEntry = {
      role: 'lawyer',
      text: argument.trim(),
    };

    try {
      const res = await axios.post('http://localhost:8000/simulate', {
        argument: argument.trim(),
        current_verdict: state.verdict,
        current_confidence: state.confidence,
        similar_cases: result.similar_cases,
        round_number: state.round,
        current_rules: result.triggered_rules || [],
        top_keywords: result.top_keywords || [],
      });

      const aiEntry = {
        role: 'ai',
        text: res.data.ai_response,
        category: res.data.argument_category,
        evidencePoints: res.data.evidence_points || [],
        verdict: res.data.updated_verdict,
        confidence: res.data.updated_confidence,
      };

      setHistory((prev) => [...prev, lawyerEntry, aiEntry]);
      setState({
        verdict: res.data.updated_verdict,
        confidence: res.data.updated_confidence,
        round: state.round + 1,
      });
      setArgument('');
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Could not run the simulator. Make sure the backend is available.'
      );
    } finally {
      setLoading(false);
    }
  };

  const confidencePct = (state.confidence * 100).toFixed(1);
  const isAccepted = state.verdict === 'ACCEPTED';

  return (
    <div style={{
      marginTop: '24px',
      background: '#ffffff',
      border: '2px solid #e5e1d8',
      borderRadius: '16px',
      padding: '24px',
      boxShadow: '0 2px 12px rgba(15,17,23,0.06)',
    }}>
      <div style={{ marginBottom: '16px' }}>
        <h3 style={{
          fontFamily: 'Playfair Display, serif',
          fontSize: '24px',
          fontWeight: 700,
          color: '#0f1117',
          marginBottom: '4px',
        }}>
          Legal Argument Simulator
        </h3>
        <p style={{
          fontSize: '13px',
          color: '#9ca3af',
          lineHeight: '1.7',
        }}>
          Challenge the prediction with a legal argument. The simulator now uses retrieved cases,
          model focus terms, and triggered legal rules to explain why confidence shifts.
        </p>
      </div>

      <div style={{
        padding: '14px 16px',
        borderRadius: '12px',
        border: '1px solid #e5e1d8',
        background: '#f7f5f0',
        marginBottom: '18px',
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          gap: '16px',
          marginBottom: '8px',
          flexWrap: 'wrap',
        }}>
          <span style={{ fontFamily: 'DM Mono, monospace', fontSize: '11px', color: '#9ca3af' }}>
            Live Prediction
          </span>
          <span style={{ fontFamily: 'DM Mono, monospace', fontSize: '11px', color: '#9ca3af' }}>
            Round {state.round}
          </span>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '14px',
        }}>
          <strong style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: '28px',
            color: isAccepted ? '#166534' : '#991b1b',
          }}>
            {state.verdict}
          </strong>
          <span style={{
            fontFamily: 'DM Mono, monospace',
            fontSize: '13px',
            color: '#6b7280',
          }}>
            {confidencePct}% confidence
          </span>
        </div>
      </div>

      {history.length > 0 && (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          marginBottom: '18px',
        }}>
          {history.map((entry, index) => (
            <div key={index} style={{
              alignSelf: entry.role === 'lawyer' ? 'flex-end' : 'stretch',
              maxWidth: entry.role === 'lawyer' ? '82%' : '100%',
              padding: '14px 16px',
              borderRadius: '14px',
              background: entry.role === 'lawyer' ? '#0f1117' : '#f7f5f0',
              color: entry.role === 'lawyer' ? '#ffffff' : '#374151',
              border: entry.role === 'lawyer' ? 'none' : '1px solid #e5e1d8',
            }}>
              <div style={{
                fontFamily: 'DM Mono, monospace',
                fontSize: '10px',
                color: entry.role === 'lawyer' ? 'rgba(255,255,255,0.7)' : '#9ca3af',
                marginBottom: '8px',
              }}>
                {entry.role === 'lawyer' ? 'Lawyer Argument' : `Simulator Response${entry.category ? ` · ${entry.category}` : ''}`}
              </div>
              <div style={{ fontSize: '13px', lineHeight: '1.7' }}>{entry.text}</div>
              {entry.evidencePoints?.length > 0 && (
                <div style={{ marginTop: '10px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {entry.evidencePoints.map((point, pointIndex) => (
                    <span key={pointIndex} style={{
                      fontSize: '11px',
                      color: '#6b7280',
                      fontFamily: 'DM Mono, monospace',
                    }}>
                      {point}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <textarea
        value={argument}
        onChange={(e) => setArgument(e.target.value)}
        placeholder="Type your legal argument here..."
        style={{
          width: '100%',
          minHeight: '130px',
          padding: '16px',
          fontSize: '13px',
          fontFamily: 'DM Mono, monospace',
          background: '#f7f5f0',
          border: '1.5px solid #e5e1d8',
          borderRadius: '12px',
          resize: 'vertical',
          outline: 'none',
          color: '#0f1117',
          lineHeight: '1.7',
        }}
      />

      {error && (
        <div style={{
          marginTop: '12px',
          padding: '12px 16px',
          background: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '10px',
          fontSize: '13px',
          color: '#991b1b',
        }}>
          {error}
        </div>
      )}

      <div style={{
        marginTop: '16px',
        display: 'flex',
        justifyContent: 'space-between',
        gap: '16px',
        alignItems: 'center',
        flexWrap: 'wrap',
      }}>
        <span style={{
          fontSize: '11px',
          color: '#9ca3af',
          fontFamily: 'DM Mono, monospace',
        }}>
          Cite procedural defects, evidence weaknesses, constitutional grounds, or lower-court errors.
        </span>
        <button
          type="button"
          onClick={submitArgument}
          disabled={loading}
          style={{
            padding: '12px 18px',
            background: loading ? '#d1cfc9' : '#0f1117',
            color: '#ffffff',
            border: 'none',
            borderRadius: '12px',
            fontSize: '13px',
            fontWeight: 600,
            fontFamily: 'DM Sans, sans-serif',
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Analyzing...' : 'Submit Argument'}
        </button>
      </div>
    </div>
  );
}
