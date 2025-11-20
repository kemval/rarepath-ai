#!/bin/bash

# RarePath AI - Cloud Run Deployment Script
# This script deploys the Streamlit app to Google Cloud Run

set -e  # Exit on error

# Add gcloud to PATH
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

echo "🚀 Starting RarePath AI deployment to Cloud Run..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"rarepath"}  # Default to the project we just created
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="rarepath-ai"
GEMINI_API_KEY=${GEMINI_API_KEY:-""}

# Step 1: Check prerequisites
echo -e "${BLUE}📋 Step 1: Checking prerequisites...${NC}"

# Verify gcloud is available
if ! command -v gcloud &> /dev/null; then
    echo -e "${YELLOW}⚠️  gcloud CLI not found in PATH. Adding it now...${NC}"
    export PATH="$HOME/google-cloud-sdk/bin:$PATH"
    
    # Check again
    if ! command -v gcloud &> /dev/null; then
        echo -e "${YELLOW}⚠️  gcloud CLI still not found. Please ensure it's installed.${NC}"
        exit 1
    fi
fi

echo "Using project: $PROJECT_ID"

if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  GEMINI_API_KEY not set in environment${NC}"
    read -p "Enter your Gemini API Key: " GEMINI_API_KEY
fi

echo -e "${GREEN}✓ Prerequisites checked${NC}"
echo ""

# Step 2: Set GCP project
echo -e "${BLUE}📋 Step 2: Setting GCP project...${NC}"
gcloud config set project $PROJECT_ID
echo -e "${GREEN}✓ Project set to: $PROJECT_ID${NC}"
echo ""

# Step 3: Enable required APIs
echo -e "${BLUE}📋 Step 3: Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
echo -e "${GREEN}✓ APIs enabled${NC}"
echo ""

# Step 4: Build and deploy
echo -e "${BLUE}📋 Step 4: Deploying to Cloud Run...${NC}"
echo "This may take 3-5 minutes..."
echo ""

gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY="$GEMINI_API_KEY" \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""

# Step 5: Get service URL
echo -e "${BLUE}📋 Step 5: Getting service URL...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 SUCCESS!${NC}"
echo "=========================================="
echo ""
echo "Your RarePath AI app is live at:"
echo -e "${GREEN}$SERVICE_URL${NC}"
echo ""
echo "Use this URL in your Kaggle capstone submission!"
echo ""
echo "To view logs:"
echo "  gcloud run logs tail $SERVICE_NAME --region $REGION"
echo ""
echo "To update deployment:"
echo "  ./deploy_cloud_run.sh"
echo ""
echo "=========================================="
