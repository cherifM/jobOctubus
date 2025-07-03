#!/bin/bash

# JobOctubus - Start Script
# This script starts both the backend (FastAPI) and frontend (React) servers

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[JobOctubus]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[JobOctubus]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[JobOctubus]${NC} $1"
}

print_error() {
    echo -e "${RED}[JobOctubus]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :"$1" >/dev/null 2>&1
}

# Function to cleanup background processes on exit
cleanup() {
    print_status "Stopping servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit
}

# Set up cleanup trap
trap cleanup SIGINT SIGTERM

print_status "Starting JobOctubus Application..."

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "backend" ]; then
    print_error "Please run this script from the JobOctubus root directory"
    exit 1
fi

# Check required commands
if ! command_exists python; then
    print_error "Python is not installed or not in PATH"
    exit 1
fi

if ! command_exists npm; then
    print_error "Node.js/npm is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Check if backend dependencies are installed
if [ ! -f "venv/lib/python*/site-packages/fastapi/__init__.py" ]; then
    print_status "Installing backend dependencies..."
    pip install -r requirements.txt
fi

# Check if frontend dependencies are installed
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install
fi

# Check environment file
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Copying from .env.example..."
    cp .env.example .env
    print_warning "Please edit .env file with your actual API keys and settings"
fi

# Check for port conflicts
if port_in_use 8000; then
    print_error "Port 8000 is already in use. Please stop the process using this port."
    exit 1
fi

if port_in_use 3000; then
    print_error "Port 3000 is already in use. Please stop the process using this port."
    exit 1
fi

print_status "Starting backend server on port 8000..."
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! port_in_use 8000; then
    print_error "Backend failed to start. Check the logs above."
    cleanup
    exit 1
fi

print_success "Backend server started successfully!"
print_status "API Documentation: http://localhost:8000/docs"

print_status "Starting frontend server on port 3000..."
npm start &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 5

print_success "Frontend server started successfully!"
print_success "Application ready!"
echo ""
print_status "🚀 JobOctubus is running:"
print_status "   Frontend: http://localhost:3000"
print_status "   Backend:  http://localhost:8000"
print_status "   API Docs: http://localhost:8000/docs"
echo ""
print_status "Press Ctrl+C to stop both servers"

# Wait for both processes
wait