# Deployment Guide: Frontend on Vercel + Backend on Render

## 🚀 Deployment Strategy
- **Frontend**: Deploy on Vercel (React/Vite)
- **Backend**: Deploy on Render (FastAPI)
- **Database**: MongoDB Atlas (cloud database)

## 📋 Prerequisites
1. **MongoDB Atlas Account** - for database
2. **Render Account** - for backend
3. **Vercel Account** - for frontend
4. **OpenAI API Key** - for AI functionality
5. **SerpAPI Key** - for web search

---

## 🔧 Step 1: Deploy Backend on Render

### 1.1 Prepare Backend Files
Your backend is already prepared with:
- ✅ `api/main.py` - FastAPI application
- ✅ `requirements.txt` - Python dependencies
- ✅ `render.yaml` - Render configuration

### 1.2 Deploy to Render
1. **Go to [Render Dashboard](https://dashboard.render.com)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service:**
   - **Name**: `aria-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: Leave empty (or `./`)

### 1.3 Set Environment Variables on Render
Add these environment variables in Render dashboard:
```
OPENAI_API_KEY=your_openai_api_key
SERPAPI_KEY=your_serpapi_key
MONGODB_URI=your_mongodb_atlas_connection_string
USE_MONGODB=true
```

### 1.4 Get Your Render Backend URL
After deployment, you'll get a URL like:
`https://aria-backend-xyz.onrender.com`

---

## 🌐 Step 2: Deploy Frontend on Vercel

### 2.1 Update Frontend Environment
1. **Go to your Vercel dashboard**
2. **Add environment variable:**
   - **Name**: `VITE_API_URL`
   - **Value**: `https://your-render-backend-url.onrender.com`
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
- **Check Render logs** for deployment errors
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

### Render (Backend)
```
OPENAI_API_KEY=sk-...
SERPAPI_KEY=your_serpapi_key
MONGODB_URI=mongodb+srv://...
USE_MONGODB=true
```

### Vercel (Frontend)
```
VITE_API_URL=https://your-render-backend-url.onrender.com
```

---

## 🎉 Success!
After deployment:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://aria-backend-xyz.onrender.com`
- **Database**: MongoDB Atlas

Your full-stack application is now live! 🚀 