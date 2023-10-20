import logo from './logo.svg';
import './App.css';
import { useState } from 'react';
import React, { useEffect } from "react";

const backendUrl = 'http://localhost:5678';

function App() {
  const [focuserPosition, setFocuserPosition] = useState('');


  const handleFocuserPositionChange = (event) => {
    setFocuserPosition(event.target.value);

  };

  const handleSendButtonClick = () => {
    // Send request to backend with focuserPosition
    console.log(`Sending request to backend with focuserPosition: ${focuserPosition}`);

    fetch(`${backendUrl}/api/focus_position`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ focuserPosition })
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        console.log('Response from backend:', data);
      })
      .catch(error => {
        console.error('Error sending request to backend:', error);
      });
  };


  const [img, setImg] = useState();

  const handleAnalyzeButtonClick = async () => {
    const res = await fetch(`${backendUrl}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });
    const imageBlob = await res.blob();
    const imageObjectURL = URL.createObjectURL(imageBlob);
    setImg(imageObjectURL);
  };

  
  const handleResetButtonClick = () => {
    // Send request to backend to analyze data
    console.log('Sending request to backend to analyze data');

    fetch(`${backendUrl}/api/reset`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        console.log('Response from backend:', data);
      })
      .catch(error => {
        console.error('Error sending request to backend:', error);
      });
  };


  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <div>
          <label htmlFor="focuserPosition">Focuser Position:</label>
          <input type="text" id="focuserPosition" value={focuserPosition} onChange={handleFocuserPositionChange} />
          <button onClick={handleSendButtonClick}>Send</button>
        </div>
        <button onClick={handleAnalyzeButtonClick}>Analyze</button>
        <button onClick={handleResetButtonClick}>Reset</button>
        {img && (
          <img src={img} alt="An example image" />
        )}

      </header>
    </div>
  );
}


export default App;

