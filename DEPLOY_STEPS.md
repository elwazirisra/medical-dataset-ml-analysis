# Step-by-Step Deployment: Vercel + Railway

Follow these exact steps to deploy your application.

## Prerequisites

- GitHub account
- Code pushed to a GitHub repository
- Models trained (run `python train_models.py`)

---

## Part 1: Deploy Backend to Railway

### Step 1: Sign up for Railway

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"** or **"Login"**
3. Sign up with GitHub (recommended) - it will connect your GitHub account

### Step 2: Create a New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Authorize Railway to access your GitHub repositories
4. Select your repository: `medical-dataset-ml-analysis`

### Step 3: Configure Backend Service

1. Railway will detect your project
2. Click on the service that was created
3. Go to **Settings** tab
4. Set **Root Directory** to: `backend`
5. Railway will auto-detect Python

### Step 4: Add Environment Variables

1. In Railway, go to the **Variables** tab
2. Add these environment variables:
   - `FLASK_ENV` = `production`
   - `FRONTEND_URL` = `https://your-frontend.vercel.app` (we'll update this after deploying frontend)
   - `PORT` = (Railway sets this automatically, but you can leave it)

### Step 5: Deploy

1. Railway will automatically start deploying
2. Wait for the build to complete (usually 2-3 minutes)
3. Once deployed, Railway will show you a URL like: `https://your-app-name.up.railway.app`
4. **Copy this URL** - you'll need it for the frontend!

### Step 6: Test Backend

1. Open the Railway URL in your browser
2. Add `/api/health` to the end: `https://your-app-name.up.railway.app/api/health`
3. You should see: `{"status":"healthy"}`
4. If you see an error about models, make sure the `models/` directory is in your Git repository

### Step 7: Verify Models are Deployed

1. In Railway, go to the **Deployments** tab
2. Click on the latest deployment
3. Check the logs to see if models loaded successfully
4. You should see: `✅ Models loaded successfully!`

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Sign up for Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **"Sign Up"**
3. Sign up with GitHub (recommended) - it will connect your GitHub account

### Step 2: Import Your Project

1. Click **"Add New..."** → **"Project"**
2. Import your GitHub repository: `medical-dataset-ml-analysis`
3. Click **"Import"**

### Step 3: Configure Build Settings

Vercel will auto-detect Vite, but verify these settings:

1. **Framework Preset:** `Vite` (should be auto-detected)
2. **Root Directory:** Click **"Edit"** and set to: `frontend`
3. **Build Command:** `npm run build` (should be auto-filled)
4. **Output Directory:** `dist` (should be auto-filled)
5. **Install Command:** `npm install` (should be auto-filled)

### Step 4: Add Environment Variables

1. Scroll down to **"Environment Variables"**
2. Click **"Add"**
3. Add this variable:
   - **Name:** `VITE_API_URL`
   - **Value:** `https://your-railway-url.up.railway.app/api`
     - Replace `your-railway-url.up.railway.app` with your actual Railway URL from Part 1
   - **Environment:** Select all (Production, Preview, Development)

### Step 5: Deploy

1. Click **"Deploy"**
2. Wait for the build to complete (usually 1-2 minutes)
3. Vercel will show you a URL like: `https://your-app-name.vercel.app`
4. **Copy this URL** - you'll need it to update Railway!

### Step 6: Test Frontend

1. Open the Vercel URL in your browser
2. The app should load
3. Try navigating to different pages
4. If you see API errors, check the browser console (F12)

---

## Part 3: Connect Frontend and Backend

### Step 1: Update Railway CORS

1. Go back to Railway dashboard
2. Select your backend service
3. Go to **Variables** tab
4. Update `FRONTEND_URL` to your Vercel URL: `https://your-app-name.vercel.app`
5. Railway will automatically redeploy

### Step 2: Verify Connection

1. Go to your Vercel frontend URL
2. Open browser console (F12)
3. Check for any CORS errors
4. Try using the app - predictions should work!

---

## Troubleshooting

### Backend Issues

**Problem: Models not found**
- Solution: Make sure `models/` directory is committed to Git
- Check: `git ls-files models/` should show model files

**Problem: Port already in use**
- Solution: Railway handles this automatically, but check the logs

**Problem: CORS errors**
- Solution: Make sure `FRONTEND_URL` in Railway matches your Vercel URL exactly

### Frontend Issues

**Problem: API calls failing**
- Solution: Check `VITE_API_URL` in Vercel environment variables
- Make sure it ends with `/api`
- Check browser console for exact error

**Problem: Build fails**
- Solution: Check Vercel build logs
- Make sure all dependencies are in `package.json`
- Try building locally: `cd frontend && npm run build`

### Connection Issues

**Problem: Frontend can't reach backend**
- Check Railway URL is accessible: `https://your-railway-url.up.railway.app/api/health`
- Check Vercel environment variable `VITE_API_URL` is correct
- Check Railway `FRONTEND_URL` matches Vercel URL

---

## Quick Checklist

### Before Deployment
- [ ] Code is pushed to GitHub
- [ ] Models are trained (`python train_models.py`)
- [ ] Models directory is committed to Git
- [ ] Tested locally (both frontend and backend work)

### Backend (Railway)
- [ ] Railway account created
- [ ] Project created from GitHub
- [ ] Root directory set to `backend`
- [ ] Environment variables set
- [ ] Deployment successful
- [ ] Health endpoint works: `/api/health`
- [ ] Models loaded successfully

### Frontend (Vercel)
- [ ] Vercel account created
- [ ] Project imported from GitHub
- [ ] Root directory set to `frontend`
- [ ] `VITE_API_URL` environment variable set to Railway URL
- [ ] Deployment successful
- [ ] Frontend loads without errors

### Final Steps
- [ ] Railway `FRONTEND_URL` updated to Vercel URL
- [ ] CORS working (no errors in browser console)
- [ ] All pages work correctly
- [ ] Predictions work end-to-end

---

## URLs to Keep Handy

After deployment, you'll have:
- **Backend URL:** `https://your-app-name.up.railway.app`
- **Frontend URL:** `https://your-app-name.vercel.app`

Bookmark both for easy access!

---

## Updating Your Deployment

### To update backend:
1. Make changes to backend code
2. Commit and push to GitHub
3. Railway will automatically redeploy

### To update frontend:
1. Make changes to frontend code
2. Commit and push to GitHub
3. Vercel will automatically redeploy

### To update models:
1. Retrain models: `python train_models.py`
2. Commit the new model files to Git
3. Push to GitHub
4. Railway will redeploy with new models

---

## Cost

Both platforms offer generous free tiers:
- **Railway:** $5/month free credit (usually enough for small projects)
- **Vercel:** Free tier with unlimited deployments

For production use, you may need to upgrade, but the free tiers are perfect for demos and testing!

---

## Need Help?

- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **Railway Discord:** https://discord.gg/railway
- **Vercel Support:** https://vercel.com/support

