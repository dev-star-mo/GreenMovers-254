# Render Docker Setup Instructions

## Correct Configuration for Render

When using Docker on Render, you need to configure it correctly:

### Option 1: Root Directory = `backend` (Recommended)

1. In Render Dashboard → Your Service → Settings:
   - **Root Directory**: `backend`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `Dockerfile` (NOT `backend/Dockerfile`)
   - **Docker Context**: Leave empty or set to `.`

### Option 2: Root Directory = `.` (Root of repo)

1. In Render Dashboard → Your Service → Settings:
   - **Root Directory**: `.` (or leave empty)
   - **Environment**: `Docker`
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Docker Context**: Leave empty

## Current Setup

The Dockerfile is located at: `backend/Dockerfile`

If you set Root Directory to `backend`, use:
- Dockerfile Path: `Dockerfile`

If you set Root Directory to `.` (root), use:
- Dockerfile Path: `backend/Dockerfile`

## Verification

After setting up, the build should:
1. Clone your repository
2. Find the Dockerfile at the correct path
3. Build the Docker image
4. Start the container

If you see errors about "no such file or directory" for backend/backend, it means the paths are misconfigured.

