#!/bin/bash

echo "🚀 Starting ARIA AI Navigator..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Prerequisites check passed"

echo "📦 Installing Python dependencies..."
if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv backend/venv
fi

source backend/venv/bin/activate
pip install -r backend/requirements.txt

echo "📦 Installing Node.js dependencies..."
cd frontend/aria
npm install
cd ../..

echo "🚀 Starting FastAPI backend..."
source backend/venv/bin/activate
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

sleep 3

echo "🚀 Starting React frontend..."
cd frontend/aria
npm run dev &
FRONTEND_PID=$!
cd ../..

echo "🎉 ARIA AI Navigator is running!"
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    deactivate
    echo "✅ Servers stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

wait 