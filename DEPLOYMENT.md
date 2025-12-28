# Deployment Guide

This guide covers deploying both the React frontend and Flask backend.

## Deployment Options

### Option 1: Vercel (Frontend) + Railway/Render (Backend) - Recommended

**Frontend (Vercel):**
- Free tier available
- Automatic deployments from Git
- Great for React/Vite apps

**Backend (Railway/Render):**
- Free tier available
- Easy Python deployment
- Can handle model files

### Option 2: Netlify (Frontend) + Heroku (Backend)

**Frontend (Netlify):**
- Free tier available
- Easy deployment

**Backend (Heroku):**
- Free tier discontinued, but paid tier available
- Well-documented

### Option 3: Single Platform (Render/Railway)

Deploy both frontend and backend on the same platform.

---

## Step-by-Step Deployment

### Part 1: Deploy Backend (Flask API)

#### Using Railway

1. **Sign up at [railway.app](https://railway.app)**

2. **Create a new project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository

3. **Configure the backend:**
   - Set root directory to `backend`
   - Add environment variables (if needed)
   - Railway will auto-detect Python

4. **Add a start command:**
   - In Railway settings, add start command: `python app.py`
   - Or create a `Procfile` in the backend directory:
     ```
     web: python app.py
     ```

5. **Upload model files:**
   - Railway has persistent storage
   - You can upload models via Railway's file system or
   - Include models in Git (if under size limits) or
   - Use Railway's volume storage

6. **Set environment variables:**
   - `FLASK_ENV=production`
   - `PORT` (Railway sets this automatically)

7. **Note the backend URL:**
   - Railway will provide a URL like: `https://your-app.railway.app`
   - Copy this URL for frontend configuration

#### Using Render

1. **Sign up at [render.com](https://render.com)**

2. **Create a new Web Service:**
   - Connect your GitHub repository
   - Select "Python 3" environment
   - Set root directory to `backend`

3. **Configure:**
   - Build command: `pip install -r requirements.txt`
   - Start command: `python app.py`
   - Environment: `Python 3`

4. **Add environment variables:**
   - `PYTHON_VERSION=3.11` (or your version)

5. **Deploy:**
   - Render will build and deploy automatically
   - Note the URL: `https://your-app.onrender.com`

---

### Part 2: Deploy Frontend (React/Vite)

#### Using Vercel

1. **Sign up at [vercel.com](https://vercel.com)**

2. **Import your project:**
   - Click "New Project"
   - Import from GitHub
   - Select your repository

3. **Configure build settings:**
   - Framework Preset: `Vite`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

4. **Add environment variables:**
   - `VITE_API_URL` = Your backend URL (e.g., `https://your-app.railway.app`)

5. **Deploy:**
   - Click "Deploy"
   - Vercel will build and deploy automatically

6. **Update API configuration:**
   - After deployment, update `frontend/src/services/api.js`:
     ```javascript
     const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://your-backend-url.com/api'
     ```

#### Using Netlify

1. **Sign up at [netlify.com](https://netlify.com)**

2. **Create a new site:**
   - Connect to GitHub
   - Select your repository

3. **Configure build settings:**
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`

4. **Add environment variables:**
   - `VITE_API_URL` = Your backend URL

5. **Deploy:**
   - Click "Deploy site"

---

## Important Configuration Steps

### 1. Update CORS in Backend

Make sure your backend allows requests from your frontend domain:

```python
# In backend/app.py
from flask_cors import CORS

# For production, specify allowed origins
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://your-frontend.vercel.app",
            "http://localhost:3000"  # Keep for local dev
        ]
    }
})
```

Or for development, you can use:
```python
CORS(app, origins=["*"])  # Only for development!
```

### 2. Update Frontend API URL

Create a `.env.production` file in the `frontend` directory:

```env
VITE_API_URL=https://your-backend-url.com/api
```

### 3. Update Vite Config for Production

Update `frontend/vite.config.js`:

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: import.meta.env.VITE_API_URL || 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  },
  // Remove proxy in production build
  build: {
    outDir: 'dist',
  }
})
```

### 4. Handle Model Files

**Option A: Include in Git (if small enough)**
- Models are already in `models/` directory
- Make sure they're committed to Git

**Option B: Use Cloud Storage**
- Upload models to S3, Google Cloud Storage, etc.
- Download on backend startup

**Option C: Generate on Deploy**
- Add model training to deployment process
- Slower first deployment but always fresh models

---

## Quick Deploy Scripts

### Backend Deployment Checklist

```bash
# 1. Ensure models are trained
python train_models.py

# 2. Test backend locally
cd backend
python app.py

# 3. Check requirements.txt is up to date
pip freeze > backend/requirements.txt

# 4. Commit and push to GitHub
git add .
git commit -m "Prepare for deployment"
git push
```

### Frontend Deployment Checklist

```bash
# 1. Build frontend locally to test
cd frontend
npm install
npm run build

# 2. Test the build
npm run preview

# 3. Update environment variables
# Create .env.production with VITE_API_URL

# 4. Commit and push
git add .
git commit -m "Prepare frontend for deployment"
git push
```

---

## Environment Variables Reference

### Backend (.env or platform settings)
```
FLASK_ENV=production
PORT=5000  # Usually set by platform
```

### Frontend (.env.production)
```
VITE_API_URL=https://your-backend-url.com/api
```

---

## Troubleshooting

### CORS Errors
- Make sure backend CORS is configured for your frontend domain
- Check that backend URL is correct in frontend

### Models Not Found
- Ensure models directory is included in deployment
- Check file paths are correct (use absolute paths)
- Verify models are committed to Git or uploaded separately

### Build Failures
- Check Node.js version (Vite needs Node 16+)
- Check Python version (needs Python 3.7+)
- Verify all dependencies in requirements.txt/package.json

### API Connection Issues
- Verify backend URL is accessible
- Check environment variables are set correctly
- Test backend health endpoint: `https://your-backend.com/api/health`

---

## Recommended: Railway + Vercel

**Why this combination:**
- Both have generous free tiers
- Easy GitHub integration
- Automatic deployments
- Good documentation

**Steps:**
1. Deploy backend to Railway
2. Get Railway backend URL
3. Deploy frontend to Vercel with `VITE_API_URL` set to Railway URL
4. Update Railway CORS to allow Vercel domain
5. Done! 🎉

---

## Alternative: Single Platform Deployment

### Render (Both Frontend & Backend)

1. **Backend:**
   - Create Web Service
   - Root: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `python app.py`

2. **Frontend:**
   - Create Static Site
   - Root: `frontend`
   - Build: `npm install && npm run build`
   - Publish: `dist`

3. **Connect:**
   - Use Render's internal networking or
   - Set `VITE_API_URL` to backend Render URL

---

## Post-Deployment

1. **Test the deployment:**
   - Visit your frontend URL
   - Test all pages
   - Verify API calls work

2. **Monitor:**
   - Check platform logs for errors
   - Monitor API response times
   - Set up error tracking (optional)

3. **Update README:**
   - Add deployment URLs
   - Update any hardcoded URLs in documentation

---

## Security Notes

⚠️ **Important:**
- Never commit `.env` files with secrets
- Use platform environment variables
- Enable HTTPS (most platforms do this automatically)
- Keep dependencies updated
- Review CORS settings for production

---

## Need Help?

- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **Render Docs:** https://render.com/docs
- **Netlify Docs:** https://docs.netlify.com

