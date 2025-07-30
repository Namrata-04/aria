#!/bin/bash
echo "=== ARIA Frontend Deployment ==="

# Set Python version to avoid conflicts
echo "Setting Python version..."
echo "python 3.11.9" > .tool-versions

echo "Installing dependencies..."
npm install
echo "Building project..."
npm run build
echo "Build complete!"
ls -la dist/ 