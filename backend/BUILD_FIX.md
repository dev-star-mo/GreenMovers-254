# Build Fix for Pillow on Render

If you encounter Pillow build errors on Render, follow these steps:

## Option 1: Set Python Version to 3.11 (Recommended)

1. Go to your Render service dashboard
2. Click on "Settings"
3. Scroll down to "Python Version"
4. Select **Python 3.11**
5. Save and redeploy

The `runtime.txt` file in the backend directory should also specify Python 3.11.0.

## Option 2: Use Pre-built Wheels

If you must use Python 3.13, ensure you're using Pillow 10.3.0 or later which has better Python 3.13 support.

## Option 3: Alternative - Use Pillow-SIMD (Advanced)

If build issues persist, you can try using pillow-simd instead:

```bash
pip install pillow-simd
```

But this requires additional system dependencies and is more complex.

## Quick Fix

The easiest solution is to ensure Render uses Python 3.11:
- Check the `runtime.txt` file exists with `python-3.11.0`
- Set Python version in Render dashboard to 3.11
- Redeploy

