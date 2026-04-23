import React from 'react';

export default function LoadingSpinner() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '80px 20px',
      gap: '20px',
    }}>
      <div style={{ position: 'relative', width: '60px', height: '60px' }}>
        <div style={{
          position: 'absolute',
          inset: 0,
          borderRadius: '50%',
          border: '4px solid #e5e1d8',
        }} />
        <div style={{
          position: 'absolute',
          inset: 0,
          borderRadius: '50%',
          border: '4px solid transparent',
          borderTop: '4px solid #c9973a',
          animation: 'spin 0.9s linear infinite',
        }} />
      </div>

      <div style={{ textAlign: 'center' }}>
        <p style={{
          fontFamily: 'Playfair Display, serif',
          fontSize: '18px',
          fontWeight: 600,
          color: '#0f1117',
          marginBottom: '6px',
        }}>
          Analyzing Case...
        </p>
        <p style={{
          fontFamily: 'DM Mono, monospace',
          fontSize: '12px',
          color: '#9ca3af',
        }}>
          Predicting · Retrieving similar cases · Computing SHAP
        </p>
      </div>

      <div style={{ display: 'flex', gap: '24px' }}>
        {['Predicting', 'Retrieving', 'Explaining'].map((step, i) => (
          <div key={i} style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontFamily: 'DM Mono, monospace',
            fontSize: '11px',
            color: '#9ca3af',
          }}>
            <span style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              background: '#c9973a',
              display: 'inline-block',
              animation: `pulse 1.2s ease ${i * 0.3}s infinite`,
            }} />
            {step}
          </div>
        ))}
      </div>
    </div>
  );
}
