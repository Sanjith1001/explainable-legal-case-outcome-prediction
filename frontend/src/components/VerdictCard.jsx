import React from 'react';

export default function VerdictCard({
  verdict,
  confidence,
  confidenceBand,
  explanationText,
  explanationPoints = [],
  evidencePoints = [],
  consistencyStatus,
  uncertaintyMessage,
}) {
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
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
        marginBottom: '18px',
      }}>
        <span style={{
          padding: '5px 10px',
          borderRadius: '999px',
          fontSize: '11px',
          fontFamily: 'DM Mono, monospace',
          background: '#ffffff',
          border: '1px solid rgba(15,17,23,0.08)',
          color: '#6b7280',
        }}>
          Confidence Band: {(confidenceBand || 'unknown').toUpperCase()}
        </span>
        {consistencyStatus && (
          <span style={{
            padding: '5px 10px',
            borderRadius: '999px',
            fontSize: '11px',
            fontFamily: 'DM Mono, monospace',
            background: '#ffffff',
            border: '1px solid rgba(15,17,23,0.08)',
            color: '#6b7280',
          }}>
            {consistencyStatus}
          </span>
        )}
      </div>

      {uncertaintyMessage && (
        <div style={{
          marginBottom: '18px',
          background: '#fef3c7',
          border: '1px solid #fbbf24',
          borderRadius: '12px',
          padding: '12px 14px',
          color: '#92400e',
          fontSize: '13px',
          lineHeight: '1.65',
        }}>
          {uncertaintyMessage}
        </div>
      )}

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
        <p style={{ fontSize: '13px', color: '#374151', lineHeight: '1.7', marginBottom: explanationPoints.length ? '14px' : 0 }}>
          {explanationText}
        </p>
        {explanationPoints.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {explanationPoints.map((point, index) => (
              <div key={index} style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
                <span style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: theme.barColor,
                  marginTop: '7px',
                  flexShrink: 0,
                }} />
                <span style={{ fontSize: '13px', color: '#4b5563', lineHeight: '1.65' }}>
                  {point}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {evidencePoints.length > 0 && (
        <div style={{
          marginTop: '16px',
          background: 'rgba(255,255,255,0.45)',
          border: '1px dashed rgba(15,17,23,0.12)',
          borderRadius: '12px',
          padding: '14px 16px',
        }}>
          <p style={{
            fontFamily: 'DM Mono, monospace',
            fontSize: '10px',
            color: '#9ca3af',
            textTransform: 'uppercase',
            letterSpacing: '1.5px',
            marginBottom: '8px',
          }}>
            Evidence Summary
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
            {evidencePoints.map((point, index) => (
              <span key={index} style={{ fontSize: '12px', color: '#4b5563', lineHeight: '1.6' }}>
                {point}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
