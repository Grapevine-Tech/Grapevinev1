// frontend/src/App.jsx
import React, { useState, useEffect } from "react";
import GoogleMapReact from "google-map-react";
import axios from "axios";

const App = () => {
  const [leads, setLeads] = useState([]);
  const [zips, setZips] = useState(["78701", "78702", ...]); // 20 default
  const [radius, setRadius] = useState(false);
  const [reps, setReps] = useState([{ email: "owner@roofco.com", phone: "+15125550123", alerts: true }]);
  const [showPopup, setShowPopup] = useState(false);

  useEffect(() => {
    const fetchLeads = async () => {
      const { data } = await axios.get("http://localhost:8000/leads");
      setLeads(data);
    };
    fetchLeads();
    const interval = setInterval(fetchLeads, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const handleSettings = async () => {
    await axios.post("http://localhost:8000/settings", { zips, radius, reps });
    if (radius) setShowPopup(true);
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl">Grapevine Dashboard</h1>
      <div className="h-96 w-full">
        <GoogleMapReact
          bootstrapURLKeys={{ key: "YOUR_GOOGLE_MAPS_API_KEY" }}
          defaultCenter={{ lat: 30.2672, lng: -97.7431 }}
          defaultZoom={10}
        >
          {leads.map((lead) => (
            <Marker key={lead.id} lat={lead.data.loc[0]} lng={lead.data.loc[1]} text={lead.data.priority} />
          ))}
        </GoogleMapReact>
      </div>
      <ul className="mt-4">
        {leads.map((lead) => (
          <li key={lead.id}>{lead.data.text} - {lead.data.cluster} ({lead.data.priority})</li>
        ))}
      </ul>
      <div className="mt-4">
        <label>Zips (20 max): <input value={zips.join(",")} onChange={(e) => setZips(e.target.value.split(","))} /></label>
        <label>Radius (25mi): <input type="checkbox" checked={radius} onChange={(e) => setRadius(e.target.checked)} /></label>
        <div>
          <h2>Team Alerts (3 free, $100/extra)</h2>
          {reps.map((rep, i) => (
            <div key={i}>
              <input value={rep.email} onChange={(e) => updateRep(i, "email", e.target.value)} placeholder="Email" />
              <input value={rep.phone} onChange={(e) => updateRep(i, "phone", e.target.value)} placeholder="Phone" />
              <input type="checkbox" checked={rep.alerts} onChange={(e) => updateRep(i, "alerts", e.target.checked)} />
            </div>
          ))}
          <button onClick={() => setReps([...reps, { email: "", phone: "", alerts: true }])}>Add Rep</button>
        </div>
        <button onClick={handleSettings}>Save</button>
        {showPopup && <div className="popup">Accuracy ~85-90% with radius</div>}
      </div>
    </div>
  );
};

const Marker = ({ text }) => <div className="bg-red-500 text-white p-1">{text}</div>;
export default App;