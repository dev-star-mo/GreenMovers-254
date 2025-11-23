# Troubleshooting Guide

## Signup/Login Issues

### Issue: "Signup failed. Please try again."

This can be caused by several issues. Check the following:

### 1. Check Browser Console

Open your browser's Developer Tools (F12) and check the Console tab for error messages. Look for:
- CORS errors
- Network errors
- API connection errors

### 2. Verify Environment Variables

**In Vercel:**
1. Go to your Vercel project → Settings → Environment Variables
2. Make sure `VITE_API_URL` is set to your Render backend URL
3. Format: `https://your-app.onrender.com` (no trailing slash)
4. Redeploy after adding/changing environment variables

**In Render:**
1. Go to your Render service → Environment
2. Make sure `FRONTEND_URL` is set to your Vercel frontend URL
3. Format: `https://your-app.vercel.app` (no trailing slash)

### 3. Test API Connection

Open your browser console and check:
```javascript
// Should show your Render URL
console.log(import.meta.env.VITE_API_URL)
```

Or test directly in browser:
```
https://your-render-url.onrender.com/health
```
Should return: `{"status": "healthy", ...}`

### 4. Check CORS Configuration

If you see CORS errors in console:
- Make sure `FRONTEND_URL` in Render matches your Vercel URL exactly
- The URL should be: `https://your-app.vercel.app` (with https, no trailing slash)

### 5. Check Database Connection

If signup fails with database errors:
- Verify `DATABASE_URL` is set in Render
- Check Render logs for database connection errors
- Make sure PostgreSQL database is running

### 6. Common Error Messages

**"Cannot connect to server"**
- Check if Render service is running (free tier spins down after 15 min)
- Verify `VITE_API_URL` is correct in Vercel
- Check network tab in browser DevTools

**"Username already registered"**
- Try a different username
- This means the user was created successfully before

**"Email already registered"**
- Try a different email
- This means the user was created successfully before

**CORS errors**
- Set `FRONTEND_URL` in Render to your exact Vercel URL
- Redeploy both services

### 7. Debug Steps

1. **Check API URL:**
   - Open browser console
   - Look for "API URL:" log message
   - Verify it matches your Render URL

2. **Check Network Requests:**
   - Open Network tab in DevTools
   - Try to sign up
   - Look for the `/api/auth/register` request
   - Check if it's going to the correct URL
   - Check the response status and body

3. **Check Render Logs:**
   - Go to Render dashboard → Your service → Logs
   - Look for errors when signup is attempted
   - Check for database connection errors

4. **Test API Directly:**
   ```bash
   curl -X POST https://your-render-url.onrender.com/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "full_name": "Test User",
       "password": "test123"
     }'
   ```

### 8. Quick Fixes

**If API URL is wrong:**
1. Update `VITE_API_URL` in Vercel
2. Redeploy Vercel app

**If CORS is blocking:**
1. Set `FRONTEND_URL` in Render to your Vercel URL
2. Redeploy Render service

**If service is sleeping (free tier):**
1. Wait for first request (may take 30-60 seconds)
2. Or upgrade to paid plan for no spin-down

## Still Having Issues?

1. Check browser console for specific error messages
2. Check Render logs for backend errors
3. Verify all environment variables are set correctly
4. Test the API directly using curl or Postman
5. Make sure both services are deployed and running

