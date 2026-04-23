import React, { useState } from 'react';

function CaseCard({ caseData, index }) {
  const [open, setOpen] = useState(false);
  const isAccepted      = caseData.label === 'ACCEPTED';
  const similarity = Number(caseData?.similarity);
  const similarityText = Number.isFinite(similarity) ? `${(similarity * 100).toFixed(1)}% similar` : 'N/A';

  const theme = isAccepted
    ? { bg: '#f0fdf4', border: '#86efac', badgeBg: '#dcfce7', badgeText: '#166534' }
    : { bg: '#fef2f2', border: '#fca5a5', badgeBg: '#fee2e2', badgeText: '#991b1b' };

  return (
    <div style={{ border: `1px solid ${theme.border}`, borderRadius: '12px', overflow: 'hidden' }}>
      <div
        onClick={() => setOpen(!open)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 16px',
          background: theme.bg,
          cursor: 'pointer',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{
            width: '28px',
            height: '28px',
            borderRadius: '50%',
            background: '#ffffff',
            border: '1px solid #e5e1d8',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: 'DM Mono, monospace',
            fontSize: '11px',
            fontWeight: 700,
            color: '#9ca3af',
          }}>
            {index + 1}
          </span>

          <span style={{
            padding: '3px 10px',
            borderRadius: '999px',
            fontSize: '11px',
            fontWeight: 600,
            background: theme.badgeBg,
            color: theme.badgeText,
          }}>
            {isAccepted ? '✓' : '✗'} {caseData.label}
          </span>

          <span style={{
            fontFamily: 'DM Mono, monospace',
            fontSize: '11px',
            color: '#9ca3af',
          }}>
            {similarityText}
          </span>
        </div>

        <span style={{ color: '#9ca3af', fontSize: '12px' }}>
          {open ? '▲' : '▼'}
        </span>
      </div>

      {open && (
        <div style={{
          padding: '12px 16px',
          background: '#ffffff',
          borderTop: `1px solid ${theme.border}`,
        }}>
          <p style={{
            fontFamily: 'DM Mono, monospace',
            fontSize: '12px',
            color: '#6b7280',
            lineHeight: '1.7',
          }}>
            {caseData.text_snippet}
            <span style={{ color: '#d1d5db' }}>...</span>
          </p>
        </div>
      )}
    </div>
  );
}

export default function SimilarCases({ cases }) {
  if (!cases || cases.length === 0) return null;

  const accepted = cases.filter((c) => c.label === 'ACCEPTED').length;
  const rejected = cases.length - accepted;

  return (
    <div className="fade-up-2" style={{
      background: '#ffffff',
      border: '1px solid #e5e1d8',
      borderRadius: '16px',
      padding: '24px',
      boxShadow: '0 2px 12px rgba(15,17,23,0.06)',
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <h3 style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: '20px',
            fontWeight: 600,
            color: '#0f1117',
            marginBottom: '4px',
          }}>
            Similar Past Cases
          </h3>
          <p style={{
            fontFamily: 'DM Mono, monospace',
            fontSize: '11px',
            color: '#9ca3af',
          }}>
            InLegalBERT semantic search · FAISS index
          </p>
        </div>

        <div style={{ display: 'flex', gap: '6px' }}>
          <span style={{
            padding: '4px 10px',
            borderRadius: '999px',
            fontSize: '11px',
            fontFamily: 'DM Mono, monospace',
            background: '#dcfce7',
            color: '#166534',
            border: '1px solid #86efac',
          }}>
            {accepted} accepted
          </span>
          <span style={{
            padding: '4px 10px',
            borderRadius: '999px',
            fontSize: '11px',
            fontFamily: 'DM Mono, monospace',
            background: '#fee2e2',
            color: '#991b1b',
            border: '1px solid #fca5a5',
          }}>
            {rejected} rejected
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {cases.map((c, i) => (
          <CaseCard key={i} caseData={c} index={i} />
        ))}
      </div>

      <p style={{
        textAlign: 'center',
        marginTop: '16px',
        fontSize: '11px',
        fontFamily: 'DM Mono, monospace',
        color: '#d1d5db',
      }}>
        Click any case to expand
      </p>
    </div>
  );
}
