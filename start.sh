#!/bin/bash
# Quick start script for Protein-Disease-Therapy Map

echo "======================================"
echo "Protein-Disease-Therapy Map Starter"
echo "======================================"
echo ""

# Check if .env files exist
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Backend .env not found!"
    echo "   Please copy backend/.env.example to backend/.env and add your API key"
    exit 1
fi

if [ ! -f "protein-modeler-app/.env" ]; then
    echo "⚠️  Frontend .env not found!"
    echo "   Please copy protein-modeler-app/.env.example to protein-modeler-app/.env"
    exit 1
fi

# Check if data exists
if [ ! -f "backend/protein_disease.db" ]; then
    echo "⚠️  Database not found!"
    echo "   Please run: cd backend && python scripts/generate_data.py"
    exit 1
fi

echo "Starting Backend API..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

echo "Waiting for backend to start..."
sleep 3

echo ""
echo "Starting Frontend..."
cd protein-modeler-app
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "======================================"
echo "✅ Services Started!"
echo "======================================"
echo "Backend API:  http://localhost:8000"
echo "API Docs:     http://localhost:8000/docs"
echo "Frontend:     http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait

