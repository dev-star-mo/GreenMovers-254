# Quick Start Guide

Get your Forest Protection Dashboard up and running in minutes!

## Local Development Setup

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python run.py
```

Backend will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### 3. First Steps

1. Open `http://localhost:3000` in your browser
2. Click "Sign up" to create an account
3. After signing up, you'll be automatically logged in
4. You'll see the dashboard with an empty forest map

### 4. Test Alert Creation (from Node-RED or curl)

```bash
# Test creating an alert
curl -X POST http://localhost:8000/api/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "TEST_001",
    "sensor_name": "Test Sensor",
    "alert_time": "2024-01-15T10:30:00Z"
  }'
```

After creating an alert, refresh your dashboard to see:
- A red sensor icon on the map
- The alert in the "Unresolved Alerts" section

### 5. Resolve an Alert

1. Go to the "Alerts" tab
2. Click "Resolve Alert" on any unresolved alert
3. Fill in the form:
   - Select threat type (Real/False)
   - Enter details
   - Upload an image
4. Submit

The sensor icon will turn green and the alert will move to "Resolved Alerts".

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions to Render and Vercel.

## Node-RED Integration

See [NODE_RED_INTEGRATION.md](NODE_RED_INTEGRATION.md) for connecting your Node-RED instance.

## Troubleshooting

### Backend won't start
- Check Python version (3.8+ required)
- Verify all dependencies are installed
- Check if port 8000 is available

### Frontend can't connect to backend
- Verify backend is running
- Check `VITE_API_URL` in `.env` file
- Check CORS settings in backend

### Database errors
- For SQLite: Ensure write permissions in backend directory
- For PostgreSQL: Verify DATABASE_URL is correct

## Next Steps

1. Deploy to production (Render + Vercel)
2. Connect your Node-RED instance
3. Configure sensor locations (latitude/longitude)
4. Customize the forest map background image
5. Add more sensors and test the full workflow


