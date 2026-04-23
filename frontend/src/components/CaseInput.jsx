import React from 'react';

export default function CaseInput({
  caseText,
  setCaseText,
  inputMode,
  setInputMode,
  pdfFile,
  setPdfFile,
  onSubmit,
  loading,
  error,
}) {
  const wordCount = caseText.trim().split(/\s+/).filter(Boolean).length;
  const canSubmit = !loading && (
    inputMode === 'pdf' ? Boolean(pdfFile) : caseText.trim().length >= 50
  );

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setPdfFile(file);
  };

  return (
    <div style={{
      background: '#ffffff',
      borderRadius: '16px',
      border: '1px solid #e5e1d8',
      padding: '24px',
      boxShadow: '0 2px 12px rgba(15,17,23,0.06)',
    }}>
      <div style={{
        display: 'flex',
        gap: '4px',
        padding: '4px',
        background: '#f7f5f0',
        borderRadius: '12px',
        border: '1px solid #e5e1d8',
        marginBottom: '20px',
      }}>
        {[
          { key: 'text', label: 'Paste Case Text' },
          { key: 'pdf', label: 'Upload PDF' },
        ].map((tab) => {
          const active = inputMode === tab.key;
          return (
            <button
              key={tab.key}
              type="button"
              onClick={() => {
                setInputMode(tab.key);
                if (tab.key === 'text') setPdfFile(null);
              }}
              style={{
                flex: 1,
                padding: '10px 12px',
                border: 'none',
                borderRadius: '9px',
                background: active ? '#ffffff' : 'transparent',
                color: active ? '#0f1117' : '#9ca3af',
                fontSize: '13px',
                fontWeight: 600,
                fontFamily: 'DM Sans, sans-serif',
                cursor: 'pointer',
                boxShadow: active ? '0 1px 4px rgba(15,17,23,0.08)' : 'none',
              }}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
        <h2 style={{
          fontFamily: 'Playfair Display, serif',
          fontSize: '20px',
          fontWeight: 600,
          color: '#0f1117',
        }}>
          {inputMode === 'pdf' ? 'Upload Case PDF' : 'Enter Case Details'}
        </h2>
        {inputMode === 'text' && (
          <span style={{
            fontFamily: 'DM Mono, monospace',
            fontSize: '11px',
            color: '#9ca3af',
          }}>
            {wordCount} words
          </span>
        )}
      </div>

      <p style={{ fontSize: '13px', color: '#9ca3af', marginBottom: '16px' }}>
        {inputMode === 'pdf'
          ? 'Upload a text-based PDF of the case judgment or petition.'
          : 'Paste the full case description, facts, arguments, or judgment text.'}
      </p>

      {inputMode === 'text' ? (
        <textarea
          style={{
            width: '100%',
            height: '220px',
            padding: '16px',
            fontSize: '13px',
            fontFamily: 'DM Mono, monospace',
            background: '#f7f5f0',
            border: '1.5px solid #e5e1d8',
            borderRadius: '12px',
            resize: 'none',
            outline: 'none',
            color: '#0f1117',
            lineHeight: '1.7',
          }}
          placeholder="Paste your case text here...

Example:
The appellant filed a petition challenging the order of the High Court
which dismissed the writ petition on the ground of maintainability.
The respondent contended that the petition was barred by limitation..."
          value={caseText}
          onChange={(e) => setCaseText(e.target.value)}
          onFocus={(e) => (e.target.style.borderColor = '#c9973a')}
          onBlur={(e)  => (e.target.style.borderColor = '#e5e1d8')}
        />
      ) : (
        <label style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '220px',
          padding: '28px',
          background: '#f7f5f0',
          border: '2px dashed #e5e1d8',
          borderRadius: '12px',
          cursor: 'pointer',
          textAlign: 'center',
        }}>
          <input
            type="file"
            accept="application/pdf,.pdf"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <span style={{
            width: '52px',
            height: '52px',
            borderRadius: '14px',
            background: '#0f1117',
            color: '#c9973a',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: 'DM Mono, monospace',
            fontWeight: 700,
            marginBottom: '14px',
          }}>
            PDF
          </span>
          <strong style={{ fontSize: '15px', color: '#0f1117', marginBottom: '6px' }}>
            {pdfFile ? pdfFile.name : 'Click to choose a PDF'}
          </strong>
          <span style={{
            fontSize: '12px',
            color: pdfFile ? '#166534' : '#9ca3af',
            fontFamily: 'DM Mono, monospace',
          }}>
            {pdfFile ? 'Ready to analyze' : 'Text-based PDFs only'}
          </span>
        </label>
      )}

      {error && (
        <div style={{
          marginTop: '12px',
          padding: '12px 16px',
          background: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '10px',
          fontSize: '13px',
          color: '#991b1b',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}>
          ⚠ {error}
        </div>
      )}

      <div style={{
        marginTop: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <span style={{ fontSize: '11px', color: '#d1d5db' }}>
          {inputMode === 'pdf' ? 'Only text-based PDFs are supported' : 'Minimum 50 characters required'}
        </span>
        <button
          onClick={onSubmit}
          disabled={!canSubmit}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 24px',
            background: canSubmit ? '#0f1117' : '#d1cfc9',
            color: '#ffffff',
            border: 'none',
            borderRadius: '12px',
            fontSize: '14px',
            fontWeight: 600,
            fontFamily: 'DM Sans, sans-serif',
            cursor: canSubmit ? 'pointer' : 'not-allowed',
          }}
        >
          {loading ? (
            <>
              <span style={{
                width: '14px',
                height: '14px',
                border: '2px solid rgba(255,255,255,0.3)',
                borderTop: '2px solid #ffffff',
                borderRadius: '50%',
                display: 'inline-block',
                animation: 'spin 0.8s linear infinite',
              }} />
              Analyzing...
            </>
          ) : (
            'Predict Outcome →'
          )}
        </button>
      </div>
    </div>
  );
}
