#!/bin/bash
# AEOLUS Simulator - Google Cloud Run Deployment Script

PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="aeolus-sim"
REGION="us-central1"

echo "======================================================"
echo " Deploying AEOLUS Simulator to Google Cloud Run"
echo "======================================================"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: Google Cloud CLI (gcloud) is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Ensure user is authenticated
echo "Checking authentication..."
gcloud auth print-access-token &> /dev/null
if [ $? -ne 0 ]; then
    echo "You are not logged into Google Cloud. Please login:"
    gcloud auth login
    gcloud auth configure-docker
fi

echo "Building and Deploying container..."
# Submit build and deploy to Cloud Run directly
gcloud run deploy $SERVICE_NAME \
    --source . \
    --project $PROJECT_ID \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --port 8501

echo "======================================================"
echo " Deployment Complete!"
echo " Visit the URL provided above to see the live simulation."
