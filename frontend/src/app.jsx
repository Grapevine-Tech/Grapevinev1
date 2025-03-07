import React, { useEffect, useState } from 'react';

function App() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://grapevinev1.onrender.com/leads')
      .then(response => response.json())
      .then(data => {
        setLeads(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching leads:', error);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading leads...</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h1>Grapevine Leads</h1>
      {leads.length === 0 ? (
        <p>No leads available.</p>
      ) : (
        <ul>
          {leads.map(lead => (
            <li key={lead.id}>
              {lead.data.text} - <strong>{lead.data.priority}</strong> 
              (Cluster: {lead.data.cluster})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;