import React, { useState } from 'react';
import './App.css';

// This is the initial state for our form. These keys MUST match what the API expects.
const initialFormData = {
  timestamp: "2023-07-15T13:00:00",
  temperature_2m: 25.5,
  precipitation: 0.0,
  weather_code: 3.0,
  cloudcover_low: 10,
  cloudcover_mid: 5,
  cloudcover_high: 0,
  wind_speed_10m: 12.0
};

// This is the URL of your running Flask API
const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5001/api/predict';

function App() {
  // State to hold the form data
  const [formData, setFormData] = useState(initialFormData);
  // State to hold the prediction result
  const [prediction, setPrediction] = useState(null);
  // State for loading and error messages
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Handles changes in the input fields
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      // Convert value to number if the field is of type 'number'
      [name]: e.target.type === 'number' ? parseFloat(value) : value
    }));
  };

  // Handles the form submission
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent the page from reloading
    setIsLoading(true);
    setError('');
    setPrediction(null);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        // If the server response is not 2xx, throw an error
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setPrediction(data.predicted_solar_generation_mw);

    } catch (err) {
      setError(err.message);
      console.error("Failed to fetch prediction:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Solar Energy Forecaster ☀️</h1>
      </header>
      <main>
        <form onSubmit={handleSubmit} className="prediction-form">
          <h2>Input Weather Conditions</h2>
          <div className="form-grid">
            {/* Map over the keys of the initial form data to generate input fields */}
            {Object.keys(initialFormData).map(key => (
              <div className="form-group" key={key}>
                <label htmlFor={key}>{key.replace(/_/g, ' ')}</label>
                <input
                  type={typeof initialFormData[key] === 'number' ? 'number' : 'text'}
                  id={key}
                  name={key}
                  value={formData[key]}
                  onChange={handleChange}
                  step="0.1" // Allows for decimal inputs
                  required
                />
              </div>
            ))}
          </div>
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Predicting...' : 'Get Prediction'}
          </button>
        </form>

        <div className="results-container">
          {error && <div className="error-message">Error: {error}</div>}
          {prediction !== null && (
            <div className="prediction-result">
              <h2>Prediction:</h2>
              <p>
                <span>{prediction.toFixed(2)}</span> MW
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;