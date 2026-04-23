import React from 'react';

export default function KeywordsPanel({ keywords }) {
  if (!keywords || keywords.length === 0) return null;

  const maxAbs = Math.max(...keywords.map((k) => Math.abs(k.shap_value)));

  return (
    <div className="fade-up-1" style={{
      background: '#ffffff',
      border: '1px solid #e5e1d8',
      borderRadius: '16px',
      padding: '24px',
      boxShadow: '0 2px 12px rgba(15,17,23,0.06)',
    }}>
      <h3 style={{
        fontFamily: 'Playfair Display, serif',
        fontSize: '20px',
        fontWeight: 600,
        color: '#0f1117',
        marginBottom: '4px',
      }}>
        Key Legal Factors
      </h3>
      <p style={{
        fontFamily: 'DM Mono, monospace',
        fontSize: '11px',
        color: '#9ca3af',
        marginBottom: '20px',
      }}>
        SHAP values — words that drove this prediction
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {keywords.map((kw, i) => {
          const isPos    = kw.direction === 'supports_accepted';
          const barWidth = ((Math.abs(kw.shap_value) / maxAbs) * 100).toFixed(1);

          return (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{
                fontFamily: 'DM Mono, monospace',
                fontSize: '11px',
                color: '#d1d5db',
                width: '16px',
                textAlign: 'right',
              }}>
                {i + 1}
              </span>

              <span style={{
                fontFamily: 'DM Mono, monospace',
                fontSize: '13px',
                fontWeight: 500,
                color: '#0f1117',
                width: '140px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}>
                {kw.word}
              </span>

              <div style={{
                flex: 1,
                height: '20px',
                background: '#f3f4f6',
                borderRadius: '6px',
                overflow: 'hidden',
              }}>
                <div style={{
                  height: '100%',
                  width: `${barWidth}%`,
                  background: isPos ? '#bbf7d0' : '#fecaca',
                  borderRadius: '6px',
                  transition: `width 0.6s ease ${i * 0.05}s`,
                }} />
              </div>

              <span style={{
                fontSize: '14px',
                color: isPos ? '#166534' : '#991b1b',
                width: '16px',
                textAlign: 'center',
              }}>
                {isPos ? '↑' : '↓'}
              </span>

              <span style={{
                fontFamily: 'DM Mono, monospace',
                fontSize: '11px',
                color: isPos ? '#166534' : '#991b1b',
                width: '56px',
                textAlign: 'right',
              }}>
                {kw.shap_value > 0 ? '+' : ''}{kw.shap_value.toFixed(3)}
              </span>
            </div>
          );
        })}
      </div>

      <div style={{
        marginTop: '20px',
        paddingTop: '16px',
        borderTop: '1px solid #f3f4f6',
        display: 'flex',
        gap: '24px',
        fontSize: '11px',
        color: '#9ca3af',
        fontFamily: 'DM Mono, monospace',
      }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '12px', height: '12px', background: '#bbf7d0', borderRadius: '3px', display: 'inline-block' }} />
          Supports Accepted
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '12px', height: '12px', background: '#fecaca', borderRadius: '3px', display: 'inline-block' }} />
          Supports Rejected
        </span>
      </div>
    </div>
  );
}
