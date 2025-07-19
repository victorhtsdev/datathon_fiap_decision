import { useEffect, useState } from 'react';

export function ApiTest() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('🚀 Iniciando teste da API...');
    
    fetch('http://localhost:8000/vagas/lista')
      .then(response => {
        console.log('📡 Response:', response);
        console.log('📡 Status:', response.status);
        console.log('📡 OK:', response.ok);
        return response.json();
      })
      .then(data => {
        console.log('📦 Data:', data);
        setData(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('❌ Error:', error);
        setError(error.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Testando API...</div>;
  if (error) return <div>Erro: {error}</div>;

  return (
    <div className="p-4 bg-yellow-100 border border-yellow-400 rounded">
      <h3 className="font-bold">Teste da API</h3>
      <pre className="text-sm">{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
