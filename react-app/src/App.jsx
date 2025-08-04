import { useState } from 'react';

export default function App() {
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const ask = async () => {
    setLoading(true);
    setResult('');
    try {
      const response = await fetch('/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      const data = await response.json();
      setResult(data.result);
    } catch (err) {
      setResult(String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '1rem' }}>
      <h1>MariaDB Query UI</h1>
      <textarea
        rows="4"
        cols="50"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question about the database"
      />
      <div>
        <button onClick={ask} disabled={loading} style={{ marginTop: '0.5rem' }}>
          {loading ? 'Running...' : 'Submit'}
        </button>
      </div>
      <pre style={{ background: '#f4f4f4', padding: '0.5rem', marginTop: '1rem' }}>
        {result}
      </pre>
    </div>
  );
}

