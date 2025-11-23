# Render Deployment Fix for Cryptography/Rust Errors

If you're getting Rust/cargo errors when deploying to Render, follow these steps:

## Solution 1: Use Dockerfile (Recommended)

The Dockerfile approach ensures Python 3.11 and includes necessary build dependencies:

1. Make sure `backend/Dockerfile` exists (it should)
2. In Render dashboard:
   - Go to your service → Settings
   - Under "Build & Deploy", find "Docker"
   - Select "Docker" instead of "Buildpacks"
   - Save and redeploy

## Solution 2: Set Python Version Manually

If not using Docker:

1. In Render dashboard:
   - Go to your service → Settings
   - Find "Python Version" or "Environment"
   - Set to **Python 3.11** (NOT 3.13)
   - Save

2. Make sure `runtime.txt` exists in `backend/` with:
   ```
   python-3.11.0
   ```

3. Redeploy

## Solution 3: Use Pre-built Wheels

The requirements.txt now includes `cryptography>=41.0.0` which should use pre-built wheels. If issues persist:

1. Try updating the build command in Render to:
   ```
   pip install --upgrade pip wheel && pip install -r requirements.txt
   ```

2. Or add to requirements.txt:
   ```
   wheel
   setuptools-rust
   ```

## Solution 4: Alternative JWT Library (If all else fails)

If cryptography continues to fail, you can use PyJWT instead:

Replace in requirements.txt:
```
python-jose[cryptography]==3.3.0
```

With:
```
pyjwt[crypto]==2.8.0
```

Then update `backend/main.py` to use PyJWT instead of python-jose. But this requires code changes.

## Quick Checklist

- [ ] Python version set to 3.11 in Render dashboard
- [ ] `runtime.txt` exists with `python-3.11.0`
- [ ] Using Dockerfile OR buildpacks with correct Python version
- [ ] `cryptography>=41.0.0` in requirements.txt
- [ ] Build command includes `pip install --upgrade pip`

