# Deployment Guide

This guide will help you deploy the Forest Protection Dashboard to free hosting services.

## Prerequisites

- GitHub account
- Render account (free tier available)
- Vercel account (free tier available)

## Step 1: Push to GitHub

1. Initialize git repository (if not already done):
```bash
git init
git add .
git commit -m "Initial commit"
```

2. Create a new repository on GitHub

3. Push your code:
```bash
git remote add origin https://github.com/yourusername/forest-protection-dashboard.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy Backend to Render

1. Go to [Render Dashboard](https://dashboard.render.com)

2. Click "New +" → "Web Service"

3. Connect your GitHub repository

4. Configure the service:
   - **Name**: `forest-protection-api`
   - **Environment**: `Python 3`
   - **Python Version**: `3.11` (IMPORTANT: Set this in Render dashboard to avoid Pillow build issues)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`

5. Add Environment Variables:
   - `SECRET_KEY`: Generate a secure random string (you can use: `openssl rand -hex 32`)
   - `DATABASE_URL`: Will be provided after creating database (see step 6)

6. Create PostgreSQL Database:
   - Click "New +" → "PostgreSQL"
   - Name: `forest-protection-db`
   - Plan: Free
   - Copy the Internal Database URL
   - Add it as `DATABASE_URL` environment variable in your web service

7. Click "Create Web Service"

8. Wait for deployment to complete

9. Copy your backend URL (e.g., `https://forest-protection-api.onrender.com`)

## Step 3: Deploy Frontend to Vercel

1. Go to [Vercel Dashboard](https://vercel.com)

2. Click "Add New..." → "Project"

3. Import your GitHub repository

4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. Add Environment Variable:
   - `VITE_API_URL`: Your Render backend URL (e.g., `https://forest-protection-api.onrender.com`)

6. Click "Deploy"

7. Wait for deployment to complete

8. Copy your frontend URL (e.g., `https://forest-protection-dashboard.vercel.app`)

## Step 4: Update CORS in Backend

1. Go back to Render dashboard

2. Edit your web service

3. Update the `CORS_ORIGIN` environment variable (if you added it) or update the code:
   - In `backend/main.py`, update line 30:
   ```python
   allow_origins=["https://your-frontend-url.vercel.app", "*"]
   ```

4. Redeploy if needed

## Step 5: Configure Node-RED

In your Node-RED flow, add an HTTP Request node:

**Configuration:**
- **Method**: POST
- **URL**: `https://your-backend-url.onrender.com/api/alerts`
- **Headers**: 
  - Key: `Content-Type`
  - Value: `application/json`
- **Body**: JSON
  ```json
  {
    "sensor_id": "{{msg.sensor_id}}",
    "sensor_name": "{{msg.sensor_name}}",
    "alert_time": "{{$now}}"
  }
  ```

Replace `{{msg.sensor_id}}` and `{{msg.sensor_name}}` with the actual fields from your LoRaWAN payload.

## Testing

1. Access your frontend URL
2. Create an account
3. Test the alert creation from Node-RED
4. Verify alerts appear in the dashboard

## Troubleshooting

### Backend Issues

- **Pillow build errors**: Ensure Python version is set to 3.11 in Render dashboard (not 3.13)
- **Database connection errors**: Ensure `DATABASE_URL` is correctly set
- **CORS errors**: Update CORS origins in `main.py`
- **Port errors**: Render automatically sets `$PORT`, ensure your start command uses it

### Frontend Issues

- **API connection errors**: Verify `VITE_API_URL` is set correctly
- **Build errors**: Check Node.js version (Vercel uses Node 18 by default)

### Node-RED Issues

- **Connection refused**: Verify backend URL is correct and service is running
- **401 errors**: Alert endpoint doesn't require auth, check your request format

## Free Tier Limitations

### Render
- Web services spin down after 15 minutes of inactivity (first request may be slow)
- 750 hours/month free
- PostgreSQL database: 90 days retention

### Vercel
- 100GB bandwidth/month
- Unlimited deployments
- No serverless function time limits

## Upgrading (Optional)

For production use, consider:
- Upgrading to paid Render plan (no spin-down)
- Using a dedicated PostgreSQL database
- Adding custom domain
- Setting up monitoring and alerts


