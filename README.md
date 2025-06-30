# ☀️ Solar Forecast App

A full-stack machine learning web application for predicting solar energy generation based on weather data.  
**Live Demo:** [https://solar-app-1.onrender.com/](https://solar-app-1.onrender.com/)

---

## 🚀 Features

- **Frontend:** Modern React app for user-friendly input and results display.
- **Backend:** Flask API serving real-time ML predictions.
- **ML Model:** XGBoost regressor trained on historical solar and weather data.
- **Dockerized:** Easy deployment with Docker for both frontend and backend.
- **Cloud Deployed:** Live on Render for instant access.

---

## 🌐 Live Demo

Try the app here:  
👉 [https://solar-app-1.onrender.com/](https://solar-app-1.onrender.com/)

---

## 🖥️ Project Structure

solar-forecast-app/
│
├── backend/ # Flask API, ML model, data scripts
│ ├── app/
│ ├── scripts/
│ ├── tests/
│ ├── Dockerfile
│ └── requirements.txt
│
├── frontend/ # React app
│ ├── public/
│ ├── src/
│ ├── Dockerfile
│ ├── package.json
│ └── .env
│
├── data/ # Raw and processed data
├── notebooks/ # Jupyter notebooks for EDA
├── docker-compose.yml
└── README.md


---

## 📦 How It Works

1. **User** enters weather data in the web app.
2. **Frontend** sends data to the backend API.
3. **Backend** loads a trained XGBoost model and returns a solar generation prediction.
4. **Frontend** displays the result instantly.

---

## 🛠️ Local Development

### **Backend**
```bash
cd backend
pip install -r requirements.txt
python main.py
# API runs at http://localhost:10000 (or 5001 for local dev)
```

### **Frontend**
```bash
cd frontend
npm install
npm start
# App runs at http://localhost:3000
```

### **Environment Variables**
- Frontend: Set `REACT_APP_API_URL` in `.env` (see `.env` example in `frontend/`).

---

## 🐳 Docker

### **Build and Run with Docker Compose**
```bash
docker compose up --build
```
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend: [http://localhost:10000/health](http://localhost:10000/health)

---

## 🧪 API Endpoints

- **POST `/api/predict`**  
  Request:
  ```json
  {
    "timestamp": "2023-10-27T14:00:00",
    "temperature_2m": 20,
    "precipitation": 0,
    "weather_code": 1,
    "cloudcover_low": 10,
    "cloudcover_mid": 20,
    "cloudcover_high": 30,
    "wind_speed_10m": 5
  }
  ```
  Response:
  ```json
  {
    "predicted_solar_generation_mw": 1234.56
  }
  ```

- **GET `/health`**  
  Returns: `"API is up and running!"`

---

## 📊 Model Details

- **Algorithm:** XGBoost Regressor
- **Features:** Weather (temperature, precipitation, cloud cover, wind speed, etc.) and time (hour, day of week, month, year)
- **Performance:**  
  - Training R²: 0.94, Testing R²: 0.80
  - Training RMSE: 570.8, Testing RMSE: 1589.7

---

## 📝 Contributing

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

---

## 📄 License

MIT License

---

## 🙏 Acknowledgements

- [Render](https://render.com/) for free hosting
- [XGBoost](https://xgboost.ai/) for the ML model
- [React](https://react.dev/) and [Flask](https://flask.palletsprojects.com/) for the web stack

---

**Questions or feedback?**  
Open an issue or contact the maintainer.