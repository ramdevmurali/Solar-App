
---

## Machine Learning Details

- **Model:** XGBoost Regressor
- **Features:** Weather (temperature, precipitation, cloud cover, wind speed, etc.) and time (hour, day of week, month, year)
- **Evaluation:**
  - Training R²: 0.941, Testing R²: 0.804
  - Training RMSE: 570.80, Testing RMSE: 1589.72
  - Training MAE: 328.16, Testing MAE: 929.13
- **Feature Importance:** Most important features include hour, month, and temperature.

---

## API Endpoints

- **GET `/health`**  
  Returns a simple status message.

- **POST `/api/predict`**  
  Expects JSON input:
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
  Returns:
  ```json
  {
    "predicted_solar_generation_mw": 1234.56
  }
  ```

---

## Running the App with Docker Compose

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/solar-forecast-app.git
   cd solar-forecast-app
   ```

2. **Build and start the services:**
   ```sh
   docker compose up --build
   ```

3. **Access the app:**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend health: [http://localhost:5001/health](http://localhost:5001/health)

---

## Project Structure
solar-forecast-app/
backend/
app/
api/
models/
scripts/
tests/
requirements.txt
Dockerfile
frontend/
src/
public/
Dockerfile
data/
raw/
processed/
notebooks/
docker-compose.yml
README.md

## Testing

- Backend tests: `backend/tests/`
- Frontend tests: `frontend/src/`
- Continuous integration: GitHub Actions workflow in `.github/workflows/ci.yml`

---

## License

MIT License

---
