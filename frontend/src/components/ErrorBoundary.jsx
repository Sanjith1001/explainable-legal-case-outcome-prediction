import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, message: '' };
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      message: error?.message || 'Unexpected UI error',
    };
  }

  componentDidCatch(error, errorInfo) {
    // Keep details in console for debugging without crashing the whole app.
    // eslint-disable-next-line no-console
    console.error('UI crash caught by ErrorBoundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ minHeight: '100vh', background: '#f7f5f0', padding: '32px' }}>
          <div
            style={{
              maxWidth: '760px',
              margin: '40px auto',
              background: '#ffffff',
              border: '1px solid #fecaca',
              borderRadius: '12px',
              padding: '20px',
            }}
          >
            <h1
              style={{
                fontFamily: 'Playfair Display, serif',
                color: '#991b1b',
                fontSize: '28px',
                marginBottom: '10px',
              }}
            >
              UI Error Detected
            </h1>
            <p style={{ color: '#6b7280', marginBottom: '10px', lineHeight: 1.6 }}>
              The app hit a runtime error and was stopped safely instead of showing a white screen.
            </p>
            <p
              style={{
                background: '#fef2f2',
                border: '1px solid #fecaca',
                borderRadius: '8px',
                padding: '10px 12px',
                fontFamily: 'DM Mono, monospace',
                fontSize: '12px',
                color: '#991b1b',
              }}
            >
              {this.state.message}
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}