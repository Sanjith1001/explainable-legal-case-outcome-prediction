import React from 'react';

export default function Navbar() {
  return (
    <nav style={{
      background: '#0f1117',
      borderBottom: '3px solid #c9973a',
      padding: '16px 32px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '40px',
          height: '40px',
          background: '#c9973a',
          borderRadius: '10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '20px',
        }}>
          ⚖
        </div>
        <div>
          <h1 style={{
            fontFamily: 'Playfair Display, serif',
            color: '#ffffff',
            fontSize: '20px',
            fontWeight: 700,
          }}>
            LegalPredict AI
          </h1>
          <p style={{
            fontFamily: 'DM Mono, monospace',
            color: 'rgba(255,255,255,0.35)',
            fontSize: '10px',
            letterSpacing: '1.5px',
            textTransform: 'uppercase',
          }}>
            Indian Supreme Court · Outcome Predictor
          </p>
        </div>
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        fontFamily: 'DM Mono, monospace',
        fontSize: '11px',
        color: 'rgba(255,255,255,0.35)',
      }}>
        <span style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: '#4ade80',
          display: 'inline-block',
          animation: 'pulse 2s infinite',
        }} />
        Model Active · ILDC + InLegalBERT · 45k Cases
      </div>
    </nav>
  );
}
