# Quick Deployment Guide: Vercel + Railway

## 🚀 Fast Track (5 minutes)

### Step 1: Prepare Your Code

```bash
# 1. Make sure models are trained
python train_models.py

# 2. Make sure models are committed to Git
git add models/
git commit -m "Add trained models for deployment"
git push
```

### Step 2: Deploy Backend (Railway) - 2 minutes

1. Go to [railway.app](https://railway.app) → Sign up with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. In the service settings:
   - Set **Root Directory:** `backend`
5. Go to **Variables** tab, add:
   - `FLASK_ENV` = `production`
   - `FRONTEND_URL` = `https://placeholder.vercel.app` (we'll update this)
6. Wait for deployment (2-3 min)
7. **Copy your Railway URL** (e.g., `https://your-app.up.railway.app`)

### Step 3: Deploy Frontend (Vercel) - 2 minutes

1. Go to [vercel.com](https://vercel.com) → Sign up with GitHub
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Configure:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite (auto-detected)
5. Add Environment Variable:
   - **Name:** `VITE_API_URL`
   - **Value:** `https://your-railway-url.up.railway.app/api` (use your Railway URL)
6. Click **"Deploy"**
7. Wait for deployment (1-2 min)
8. **Copy your Vercel URL** (e.g., `https://your-app.vercel.app`)

### Step 4: Connect Them - 1 minute

1. Go back to Railway
2. Update `FRONTEND_URL` variable to your Vercel URL
3. Railway will auto-redeploy
4. Done! 🎉

---

## ✅ Test Your Deployment

1. Visit your Vercel URL
2. Test the app - all pages should work
3. Try making a prediction
4. Check browser console (F12) for any errors

---

## 🔧 Common Issues

**Models not found?**
- Make sure `models/` directory is in Git (check with `git ls-files models/`)

**CORS errors?**
- Make sure Railway `FRONTEND_URL` matches your Vercel URL exactly

**API not working?**
- Check Railway URL: `https://your-railway-url.up.railway.app/api/health`
- Verify `VITE_API_URL` in Vercel is correct

---

## 📝 Your URLs

After deployment, save these:
- **Backend:** `https://your-app.up.railway.app`
- **Frontend:** `https://your-app.vercel.app`

---

For detailed steps, see `DEPLOY_STEPS.md`

