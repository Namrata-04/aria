# Deployment Guide: Frontend on Vercel + Backend on Railway

## 🚀 Deployment Strategy
- **Frontend**: Deploy on Vercel (React/Vite)
- **Backend**: Deploy on Railway (FastAPI)
- **Database**: MongoDB Atlas (cloud database)

## 📋 Prerequisites
1. **MongoDB Atlas Account** - for database
2. **Railway Account** - for backend
3. **Vercel Account** - for frontend
4. **OpenAI API Key** - for AI functionality
5. **SerpAPI Key** - for web search

---

## 🔧 Step 1: Deploy Backend on Railway

### 1.1 Prepare Backend Files
Your backend is already prepared with:
- ✅ `api/main.py` - FastAPI application
- ✅ `requirements.txt` - Python dependencies
- ✅ `railway.json` - Railway configuration

### 1.2 Deploy to Railway
1. **Go to [Railway Dashboard](https://railway.app)**
2. **Click "New Project" → "Deploy from GitHub repo"**
3. **Connect your GitHub repository**
4. **Railway will auto-detect the configuration from `railway.json`**
5. **The service will be named automatically**

### 1.3 Set Environment Variables on Railway
Add these environment variables in Railway dashboard:
```
OPENAI_API_KEY=your_openai_api_key
SERPAPI_KEY=your_serpapi_key
MONGODB_URI=your_mongodb_atlas_connection_string
USE_MONGODB=true
```

### 1.4 Get Your Railway Backend URL
After deployment, you'll get a URL like:
`https://aria-backend-production-xyz.up.railway.app`

---

## 🌐 Step 2: Deploy Frontend on Vercel

### 2.1 Update Frontend Environment
1. **Go to your Vercel dashboard**
2. **Add environment variable:**
   - **Name**: `VITE_API_URL`
   - **Value**: `https://your-railway-backend-url.up.railway.app`
   - **Environment**: Production

### 2.2 Configure Vercel Build Settings
In your Vercel dashboard:
- **Framework Preset**: `Vite`
- **Build Command**: `npm run build`
- **Output Directory**: `frontend/aria/dist`
- **Install Command**: `npm install`

### 2.3 Deploy to Vercel
1. **Connect your GitHub repository**
2. **Vercel will auto-detect the settings**
3. **Deploy!**

---

## 🔗 Step 3: Connect Frontend to Backend

### 3.1 Update API Configuration
The frontend is already configured to use the environment variable `VITE_API_URL`.

### 3.2 Test the Connection
After deployment:
1. **Visit your Vercel frontend URL**
2. **Try creating a session**
3. **Test the research functionality**

---

## 🛠️ Troubleshooting

### Backend Issues
- **Check Railway logs** for deployment errors
- **Verify environment variables** are set correctly
- **Test backend endpoints** directly with Postman/curl

### Frontend Issues
- **Check Vercel build logs** for build errors
- **Verify `VITE_API_URL`** is set correctly
- **Check browser console** for API errors

### CORS Issues
If you get CORS errors, the backend already has CORS configured for all origins.

---

## 📝 Environment Variables Summary

### Railway (Backend)
```
OPENAI_API_KEY=sk-...
SERPAPI_KEY=your_serpapi_key
MONGODB_URI=mongodb+srv://...
USE_MONGODB=true
```

### Vercel (Frontend)
```
VITE_API_URL=https://your-railway-backend-url.up.railway.app
```

---

## 🎉 Success!
After deployment:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://aria-backend-production-xyz.up.railway.app`
- **Database**: MongoDB Atlas

Your full-stack application is now live! 🚀 