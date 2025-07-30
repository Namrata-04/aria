#!/bin/bash
echo "=== ARIA Frontend Deployment ==="
echo "Installing dependencies..."
npm install
echo "Building project..."
npm run build
echo "Build complete!"
ls -la dist/ 