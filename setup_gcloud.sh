#!/bin/bash

# RarePath AI - Quick Cloud Run Setup Script
# Run this after gcloud is installed

set -e

echo "🔧 Setting up gcloud for RarePath AI deployment..."
echo ""

# Add gcloud to PATH for this session
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

# Step 1: Initialize gcloud
echo "Step 1: Initializing gcloud (you'll need to login)"
echo "---------------------------------------------------"
gcloud init --skip-diagnostics

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: ./deploy_cloud_run.sh"
echo "2. Your app will be deployed to Cloud Run"
echo "3. You'll get a public URL for your Kaggle submission"
echo ""
