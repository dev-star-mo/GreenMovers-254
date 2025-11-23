# Forest Protection IoT Dashboard

A comprehensive dashboard for monitoring acoustic IoT sensors deployed in forests to combat illegal logging. The system receives alerts from ESP32 devices via LoRaWAN through ChirpStack and Node-RED.

## Features

- **User Authentication**: Login and signup system for forest rangers and environmental protection NGOs
- **Real-time Dashboard**: Overview map showing sensor locations with color-coded status
  - Green: No active alerts
  - Red: Active alert detected
- **Alert Management**: 
  - View unresolved and resolved alerts
  - Resolve alerts with threat classification, details, and image uploads
- **REST API**: JSON-based APIs for Node-RED integration

## Tech Stack

- **Frontend**: React with Vite
- **Backend**: Python FastAPI
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT tokens

## Project Structure

```
.
├── backend/          # Python FastAPI backend
│   ├── main.py      # Main application file
│   ├── models.py    # Database models
│   ├── schemas.py   # Pydantic schemas
│   ├── database.py  # Database configuration
│   └── requirements.txt
├── frontend/        # React frontend
│   ├── src/
│   │   ├── pages/   # Page components
│   │   ├── components/ # Reusable components
│   │   └── services/   # API services
│   └── package.json
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Sensors
- `GET /api/sensors` - Get all sensors
- `POST /api/sensors` - Create sensor

### Alerts (for Node-RED)
- `POST /api/alerts` - Create alert (no auth required for Node-RED)
  ```json
  {
    "sensor_id": "sensor_001",
    "sensor_name": "North Forest Sensor",
    "alert_time": "2024-01-15T10:30:00"
  }
  ```
- `GET /api/alerts?resolved=false` - Get unresolved alerts
- `GET /api/alerts?resolved=true` - Get resolved alerts
- `POST /api/alerts/{id}/resolve` - Resolve alert (with form data)

### Dashboard
- `GET /api/dashboard/overview` - Get dashboard overview
- `GET /api/sensors/{sensor_id}/status` - Get sensor status

## Local Development

### Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```
VITE_API_URL=http://localhost:8000
```

4. Run development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Deployment

### Backend (Render)

1. Create a new account on [Render](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - `SECRET_KEY`: Generate a secure random key
   - `DATABASE_URL`: Render will provide this if you create a PostgreSQL database
7. Deploy

### Frontend (Vercel)

1. Create a new account on [Vercel](https://vercel.com)
2. Import your GitHub repository
3. Set root directory to `frontend`
4. Add environment variable:
   - `VITE_API_URL`: Your Render backend URL (e.g., `https://your-app.onrender.com`)
5. Deploy

## Node-RED Integration

In your Node-RED flow, use an HTTP Request node to send alerts to the dashboard:

**Method**: POST  
**URL**: `https://your-backend-url.onrender.com/api/alerts`  
**Headers**: `Content-Type: application/json`  
**Body** (JSON):
```json
{
  "sensor_id": "{{sensor_id}}",
  "sensor_name": "{{sensor_name}}",
  "alert_time": "{{$now}}"
}
```

The sensor_id, sensor_name, and alert_time should be extracted from your LoRaWAN payload in Node-RED.

## Environment Variables

### Backend
- `SECRET_KEY`: Secret key for JWT token signing
- `DATABASE_URL`: Database connection string

### Frontend
- `VITE_API_URL`: Backend API URL

## License

This project is developed for forest protection and environmental conservation purposes.


