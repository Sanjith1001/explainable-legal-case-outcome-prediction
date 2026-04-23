import React from 'react';

export default function VerdictCard({ verdict, confidence, explanationText }) {
  const isAccepted = verdict === 'ACCEPTED';
  const pct = (confidence * 100).toFixed(1);

  const theme = isAccepted
    ? { bg: '#f0fdf4', border: '#86efac', iconBg: '#166534', textColor: '#166534', barColor: '#16a34a' }
    : { bg: '#fef2f2', border: '#fca5a5', iconBg: '#991b1b', textColor: '#991b1b', barColor: '#dc2626' };

  return (
    <div className="fade-up" style={{
      background: theme.bg,
      border: `2px solid ${theme.border}`,
      borderRadius: '16px',
      padding: '24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' }}>
        <div style={{
          width: '56px',
          height: '56px',
          background: theme.iconBg,
          borderRadius: '16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '28px',
          color: '#ffffff',
        }}>
          {isAccepted ? '✓' : '✗'}
        </div>
        <div>
          <p style={{
            fontFamily: 'DM Mono, monospace',
            fontSize: '10px',
            color: '#9ca3af',
            textTransform: 'uppercase',
            letterSpacing: '1.5px',
            marginBottom: '4px',
          }}>
            Predicted Outcome
          </p>
          <h2 style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: '36px',
            fontWeight: 700,
            color: theme.textColor,
          }}>
            {verdict}
          </h2>
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ fontFamily: 'DM Mono, monospace', fontSize: '11px', color: '#9ca3af' }}>
            Confidence Score
          </span>
          <span style={{
            fontFamily: 'DM Mono, monospace',
            fontSize: '13px',
            fontWeight: 600,
            color: theme.textColor,
          }}>
            {pct}%
          </span>
        </div>
        <div style={{
          height: '10px',
          background: 'rgba(255,255,255,0.7)',
          borderRadius: '999px',
          overflow: 'hidden',
        }}>
          <div style={{
            height: '100%',
            width: `${pct}%`,
            background: theme.barColor,
            borderRadius: '999px',
            transition: 'width 1s ease',
          }} />
        </div>
      </div>

      <div style={{
        background: 'rgba(255,255,255,0.6)',
        border: '1px solid rgba(255,255,255,0.8)',
        borderRadius: '12px',
        padding: '16px',
      }}>
        <p style={{
          fontFamily: 'DM Mono, monospace',
          fontSize: '10px',
          color: '#9ca3af',
          textTransform: 'uppercase',
          letterSpacing: '1.5px',
          marginBottom: '8px',
        }}>
          AI Explanation
        </p>
        <p style={{ fontSize: '13px', color: '#374151', lineHeight: '1.7' }}>
          {explanationText}
        </p>
      </div>
    </div>
  );
}
